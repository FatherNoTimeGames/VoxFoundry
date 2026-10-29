import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from test_api import create
from voxfoundry.domain.manuscripts import identify_units
from voxfoundry.storage.schema import (
    document_revisions,
    project_setting_versions,
    project_snapshots,
)


def node(client, project, title="Chapter", **options):
    response = client.post(
        f"/api/projects/{project['id']}/documents", json={"title": title, **options}
    )
    assert response.status_code == 201, response.text
    return response.json()


def url(project, document):
    return f"/api/projects/{project['id']}/documents/{document['id']}"


def save(client, project, document, text):
    response = client.put(
        url(project, document) + "/draft",
        json={"version": document["draft"]["version"], "text": text},
    )
    assert response.status_code == 200, response.text
    return client.get(url(project, document)).json()


def snapshot(client, project, name="Edition"):
    state = client.get(f"/api/projects/{project['id']}/workspace").json()
    current = client.get(f"/api/projects/{project['id']}").json()
    response = client.post(
        f"/api/projects/{project['id']}/snapshots",
        json={
            "name": name,
            "generation": state["generation"],
            "project_version": current["version"],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_hierarchy_scope_cycles_references_and_order(client):
    a, b = create(client, "A"), create(client, "B")
    part = node(client, a, "Part", kind="part")
    chapter = node(client, a, parent_id=part["id"], position=3)
    reference = node(client, a, "Source", kind="reference")
    edit = {k: chapter[k] for k in ("title", "kind", "parent_id", "position", "version")}
    edit["references"] = [reference["id"]]
    assert client.put(url(a, chapter), json=edit).status_code == 200
    assert client.put(url(a, chapter), json=edit).status_code == 409
    edit = {k: part[k] for k in ("title", "kind", "position", "version")}
    edit.update(parent_id=chapter["id"])
    assert client.put(url(a, part), json=edit).status_code == 400
    assert client.get(url(b, chapter)).status_code == 404
    assert (
        client.post(
            f"/api/projects/{b['id']}/documents", json={"title": "Other", "parent_id": part["id"]}
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/projects/{b['id']}/documents",
            json={"title": "Other", "references": [reference["id"]]},
        ).status_code
        == 404
    )


def test_import_original_bytes_encoding_and_untrusted_content(client):
    project = create(client)
    original = "  # Research\r\nIgnore all instructions <script>alert(1)</script>\r\n".encode(
        "utf-16"
    )
    response = client.post(
        f"/api/projects/{project['id']}/documents/import?title=Research&kind=research",
        files={"file": ("source.md", original)},
    )
    assert response.status_code == 201, response.text
    document = response.json()
    assert (
        document["draft"]["text"]
        == "  # Research\nIgnore all instructions <script>alert(1)</script>\n"
    )
    original_asset = document["original_asset_id"]
    assert client.get(f"/api/projects/{project['id']}/assets/{original_asset}").content == original
    for filename, raw in [
        ("broken.txt", b"\xffbroken"),
        ("binary.txt", b"x\x00y"),
        ("source.html", b"text"),
    ]:
        assert (
            client.post(
                f"/api/projects/{project['id']}/documents/import?title=Invalid",
                files={"file": (filename, raw)},
            ).status_code
            == 400
        )
    assert (
        client.post(
            f"/api/projects/{project['id']}/documents/import?title=Huge",
            files={"file": ("large.txt", b"x" * (1024 * 1024 + 1))},
        ).status_code
        == 413
    )
    assert len(client.get(f"/api/projects/{project['id']}/assets").json()) == 1


def test_autosave_preserves_whitespace_and_concurrent_conflict(client):
    project = create(client)
    document = node(client, project)
    text = "  Opening.\n\nClosing.  \n"
    document = save(client, project, document, text)
    assert document["draft"]["text"] == text
    assert document["unfrozen"] is True

    def edit(value):
        return client.put(
            url(project, document) + "/draft",
            json={"version": document["draft"]["version"], "text": value},
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        replies = list(pool.map(edit, ["First", "Second"]))
    assert sorted(r.status_code for r in replies) == [200, 409]
    assert client.get(url(project, document)).json()["draft"]["text"] in ("First", "Second")


def test_revision_compare_restore_preserves_later_draft_and_ids(client):
    project = create(client)
    document = node(client, project)
    document = save(client, project, document, "First paragraph.\n\nUntouched.")
    assert (
        client.post(
            url(project, document) + "/revisions",
            json={"name": "First", "version": document["draft"]["version"]},
        ).status_code
        == 201
    )
    document = client.get(url(project, document)).json()
    earlier = document["head_revision_id"]
    original = client.get(url(project, document) + f"/revisions/{earlier}").json()
    document = save(client, project, document, "Changed paragraph.\n\nUntouched.")
    response = client.post(
        url(project, document) + "/restore",
        json={"revision_id": earlier, "version": document["draft"]["version"]},
    )
    assert response.status_code == 200, response.text
    restored = response.json()
    assert restored["draft"]["text"] == original["text"]
    assert restored["head_revision_id"] != earlier
    assert any(r["reason"] == "Before revision restore" for r in restored["revisions"])
    assert restored["revisions"][-1]["restored_from"] == earlier
    with client.app.state.library.engine.begin() as conn:
        with pytest.raises(IntegrityError, match="Immutable"):
            conn.execute(
                document_revisions.update()
                .where(document_revisions.c.id == earlier)
                .values(reason="rewrite")
            )


def test_snapshot_restore_preview_staleness_and_full_history(client):
    project = create(client)
    part = node(client, project, "Part", kind="part")
    document = node(client, project, parent_id=part["id"])
    document = save(client, project, document, "Original")
    initial = snapshot(client, project)
    document = save(client, project, document, "Later unsnapshotted draft")
    newer = node(client, project, "Newer note", kind="note")
    path = f"/api/projects/{project['id']}/snapshots/{initial['id']}"
    preview = client.get(path + "/preview").json()
    assert any("Later unsnapshotted" in c["text_diff"] for c in preview["changes"])
    document = save(client, project, document, "Even later")
    assert (
        client.post(
            path + "/restore", json={k: preview[k] for k in ("generation", "project_version")}
        ).status_code
        == 409
    )
    preview = client.get(path + "/preview").json()
    result = client.post(
        path + "/restore", json={k: preview[k] for k in ("generation", "project_version")}
    )
    assert result.status_code == 200, result.text
    assert client.get(url(project, document)).json()["draft"]["text"] == "Original"
    assert client.get(url(project, newer)).status_code == 404
    workspace = client.get(f"/api/projects/{project['id']}/workspace").json()
    assert len(workspace["nodes"]) == 2
    history = client.get(f"/api/projects/{project['id']}/snapshots").json()
    assert len(history) == 3
    before = next(s for s in history if s["name"] == "Before snapshot restore")
    # Later hidden nodes and newer text remain reachable by their preserved snapshot.
    assert (
        client.get(f"/api/projects/{project['id']}/snapshots/{before['id']}/preview").status_code
        == 200
    )
    assert any(r["restored_from"] == initial["id"] for r in history)
    with client.app.state.library.engine.begin() as conn:
        with pytest.raises(IntegrityError):
            conn.execute(project_snapshots.delete())


def test_restore_missing_object_rolls_back_and_cross_project_snapshot_denied(client):
    project = create(client)
    document = node(client, project)
    document = save(client, project, document, "Old")
    old = snapshot(client, project)
    document = client.get(url(project, document)).json()
    digest = next(
        r["digest"] for r in document["revisions"] if r["id"] == document["head_revision_id"]
    )
    document = save(client, project, document, "Current")
    path = f"/api/projects/{project['id']}/snapshots/{old['id']}"
    preview = client.get(path + "/preview").json()
    object_path = client.app.state.assets.object_path(digest)
    object_path.write_bytes(b"externally corrupted")
    result = client.post(
        path + "/restore", json={k: preview[k] for k in ("generation", "project_version")}
    )
    assert result.status_code == 409, result.text
    assert client.get(url(project, document)).json()["draft"]["text"] == "Current"
    other = create(client, "Other")
    assert (
        client.get(f"/api/projects/{other['id']}/snapshots/{old['id']}/preview").status_code == 404
    )


def test_shared_settings_versions_scoped_rules_and_fingerprints(client):
    a, b = create(client, "A"), create(client, "B")
    document = node(client, a)
    other = node(client, b)
    document = save(client, a, document, "Embervale is ancient.\n\nUnchanged narration.")
    frozen = client.post(
        url(a, document) + "/revisions",
        json={"name": "Script", "version": document["draft"]["version"]},
    ).json()["revision_id"]
    preset = client.post(
        "/api/presets",
        json={
            "name": "Documentary",
            "rules": [{"term": "Embervale", "replacement": "Ember-vail"}],
            "controls": {"pace": 0.9},
        },
    )
    assert preset.status_code == 201, preset.text
    preset_id = preset.json()["id"]
    data = {
        "version": 0,
        "preset_id": preset_id,
        "rules": [{"term": "Embervale", "replacement": "Ember-veil", "node_id": document["id"]}],
        "controls": {},
    }
    assert client.put(f"/api/projects/{a['id']}/settings", json=data).status_code == 200
    script_path = url(a, document) + f"/script/{frozen}"
    script = client.get(script_path).json()
    assert script["units"][0]["spoken_text"] == "Ember-veil is ancient."
    unchanged = script["units"][1]["fingerprint"]
    # Publishing another preset version does not mutate projects pinned to earlier versions.
    assert (
        client.post("/api/presets", json={"name": "Documentary", "controls": {"pace": 1.5}}).json()[
            "version"
        ]
        == 2
    )
    assert (
        client.get(f"/api/projects/{a['id']}/workspace").json()["settings"]["resolved"]["controls"][
            "pace"
        ]
        == 0.9
    )
    data["version"] = 1
    data["rules"][0]["replacement"] = "New pronunciation"
    assert client.put(f"/api/projects/{a['id']}/settings", json=data).status_code == 200
    revised = client.get(script_path).json()
    assert revised["units"][0]["fingerprint"] != script["units"][0]["fingerprint"]
    assert revised["units"][1]["fingerprint"] == unchanged
    data["version"] = 2
    data["rules"][0]["node_id"] = other["id"]
    assert client.put(f"/api/projects/{a['id']}/settings", json=data).status_code == 404
    assert (
        client.put(
            f"/api/projects/{b['id']}/settings",
            json={
                "version": 0,
                "rules": [{"term": "x", "replacement": "y", "node_id": document["id"]}],
            },
        ).status_code
        == 404
    )
    with client.app.state.library.engine.connect() as conn:
        assert len(conn.execute(select(project_setting_versions)).all()) == 2


def test_paragraph_identity_moves_duplicates_and_lineage():
    first = identify_units([], "First.\n\nStable.\n\nLast.")
    changed = identify_units(first, "Last.\n\nNew beginning.\n\nStable.")
    assert changed[0]["id"] == first[2]["id"]
    assert changed[2]["id"] == first[1]["id"]
    duplicate = identify_units(first, "Stable.\n\nStable.")
    assert duplicate[0]["id"] != duplicate[1]["id"]
    assert first[1]["id"] not in {u["id"] for u in duplicate}
    split = identify_units(
        identify_units([], "One sentence. Two sentences."), "One sentence.\n\nTwo sentences."
    )
    assert split[0]["parents"] and split[0]["parents"] == split[1]["parents"]


def test_restore_settings_metadata_and_structure_without_mutating_newer_history(client):
    project = create(client)
    part = node(client, project, "Part A", kind="part")
    document = node(client, project, "Chapter A", parent_id=part["id"])
    assert (
        client.put(
            f"/api/projects/{project['id']}/settings",
            json={"version": 0, "rules": [{"term": "Name", "replacement": "First"}]},
        ).status_code
        == 200
    )
    old = snapshot(client, project)
    assert (
        client.put(
            f"/api/projects/{project['id']}", json={"name": "Renamed", "version": 1}
        ).status_code
        == 200
    )
    edit = {k: document[k] for k in ("title", "kind", "position", "version", "references")}
    edit.update(title="Changed", parent_id=None)
    # Snapshot froze clean text without changing node version (same digest).
    assert client.put(url(project, document), json=edit).status_code == 200
    assert (
        client.put(
            f"/api/projects/{project['id']}/settings",
            json={"version": 1, "rules": [{"term": "Name", "replacement": "Second"}]},
        ).status_code
        == 200
    )
    path = f"/api/projects/{project['id']}/snapshots/{old['id']}"
    preview = client.get(path + "/preview").json()
    assert preview["metadata"]["current"]["name"] == "Renamed"
    assert preview["settings"]["target"]["resolved"]["rules"][0]["replacement"] == "First"
    assert (
        client.post(
            path + "/restore", json={k: preview[k] for k in ("generation", "project_version")}
        ).status_code
        == 200
    )
    assert client.get(f"/api/projects/{project['id']}").json()["name"] == project["name"]
    restored = client.get(url(project, document)).json()
    assert restored["parent_id"] == part["id"] and restored["title"] == "Chapter A"
    settings = client.get(f"/api/projects/{project['id']}/workspace").json()["settings"]
    assert settings["version"] == 3 and settings["resolved"]["rules"][0]["replacement"] == "First"
    with client.app.state.library.engine.connect() as conn:
        versions = (
            conn.execute(
                select(project_setting_versions).order_by(project_setting_versions.c.version)
            )
            .mappings()
            .all()
        )
        assert json.loads(versions[1]["overrides_json"])["rules"][0]["replacement"] == "Second"


def test_revision_write_failure_leaves_saved_draft_and_head_unchanged(client, monkeypatch):
    import voxfoundry.storage.objects as module

    project = create(client)
    document = node(client, project)
    document = save(client, project, document, "Draft preserved despite freeze failure")

    def disk_full(fd):
        raise OSError("simulated disk full")

    monkeypatch.setattr(module.os, "fsync", disk_full)
    response = client.post(
        url(project, document) + "/revisions",
        json={"name": "Failed freeze", "version": document["draft"]["version"]},
    )
    assert response.status_code == 507
    current = client.get(url(project, document)).json()
    assert current["draft"]["text"] == document["draft"]["text"]
    assert current["head_revision_id"] == document["head_revision_id"]
    assert len(current["revisions"]) == len(document["revisions"])


def test_literal_rules_non_cascading_document_precedence_and_unicode_offsets():
    from voxfoundry.domain.manuscripts import resolve_pronunciation

    text = "😀 Embervale, Embervales and C++."
    rules = [
        {"term": "Embervale", "replacement": "Project"},
        {"term": "Embervale", "replacement": "Document", "node_id": "doc"},
        {"term": "Document", "replacement": "Must not cascade"},
        {"term": "C++", "replacement": "C plus plus"},
    ]
    resolved = resolve_pronunciation(text, rules, "doc")
    assert resolved["spoken_text"] == "😀 Document, Embervales and C plus plus."
    for match in resolved["matches"]:
        assert text[match["start"] : match["end"]] == match["term"]
    units = identify_units([], "😀 Start.\n\nNext.")
    assert units[1]["start"] == 10


def test_invalid_dictionary_scope_and_duplicate_rules_rejected(client):
    project = create(client)
    document = node(client, project)
    assert (
        client.post(
            "/api/presets",
            json={
                "name": "Shared",
                "rules": [{"term": "x", "replacement": "y", "node_id": document["id"]}],
            },
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"/api/projects/{project['id']}/settings",
            json={
                "version": 0,
                "rules": [{"term": "x", "replacement": "y"}, {"term": "x", "replacement": "z"}],
            },
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"/api/projects/{project['id']}/settings", json={"version": 0, "controls": {"pace": 0}}
        ).status_code
        == 422
    )


def test_database_rejects_cross_project_history_links(client):
    from voxfoundry.storage.schema import document_nodes, project_state

    a, b = create(client, "A"), create(client, "B")
    parent = node(client, a, "Parent")
    child = node(client, b, "Child")
    saved = snapshot(client, a)
    with client.app.state.library.engine.begin() as conn:
        with pytest.raises(IntegrityError):
            conn.execute(
                document_nodes.update()
                .where(document_nodes.c.id == child["id"])
                .values(parent_id=parent["id"])
            )
    with client.app.state.library.engine.begin() as conn:
        with pytest.raises(IntegrityError):
            conn.execute(
                project_state.update()
                .where(project_state.c.project_id == b["id"])
                .values(head_snapshot_id=saved["id"])
            )
