import hashlib
import json
from contextlib import contextmanager
from difflib import unified_diff
from uuid import uuid4

from sqlalchemy import func, select
from voxfoundry.domain.errors import DomainError
from voxfoundry.domain.manuscripts import (
    canonical,
    decode_import,
    identify_units,
    resolve_pronunciation,
    validate_text,
)
from voxfoundry.storage.assets import fingerprint
from voxfoundry.storage.library import timestamp
from voxfoundry.storage.objects import TextObjects
from voxfoundry.storage.schema import (
    assets,
    blobs,
    projects,
    series,
)
from voxfoundry.storage.schema import (
    document_drafts as drafts,
)
from voxfoundry.storage.schema import (
    document_nodes as nodes,
)
from voxfoundry.storage.schema import (
    document_revisions as revisions,
)
from voxfoundry.storage.schema import (
    preset_versions as presets,
)
from voxfoundry.storage.schema import (
    project_setting_versions as settings_history,
)
from voxfoundry.storage.schema import (
    project_settings as settings,
)
from voxfoundry.storage.schema import (
    project_snapshots as snapshots,
)
from voxfoundry.storage.schema import (
    project_state as states,
)


class Manuscripts:
    def __init__(self, library, asset_store):
        self.library = library
        self.assets = asset_store
        self.objects = TextObjects(asset_store)

    @contextmanager
    def transaction(self, project_id, *, write=True):
        with self.library.engine.begin() as conn:
            conn.exec_driver_sql("BEGIN IMMEDIATE" if write else "BEGIN")
            project = (
                conn.execute(select(projects).where(projects.c.id == project_id)).mappings().first()
            )
            if not project or (write and project["trashed_at"]):
                raise DomainError("Active project not found", 404)
            yield conn

    @staticmethod
    def state(conn, project_id):
        row = (
            conn.execute(select(states).where(states.c.project_id == project_id)).mappings().first()
        )
        return (
            dict(row)
            if row
            else {"project_id": project_id, "generation": 0, "head_snapshot_id": None}
        )

    def bump(self, conn, project_id, snapshot_id=None):
        state = self.state(conn, project_id)
        changes = {
            "generation": state["generation"] + 1,
            "head_snapshot_id": snapshot_id or state["head_snapshot_id"],
        }
        if state["generation"]:
            conn.execute(states.update().where(states.c.project_id == project_id).values(**changes))
        else:
            conn.execute(states.insert().values(project_id=project_id, **changes))

    @staticmethod
    def node(conn, project_id, node_id, active=True):
        row = (
            conn.execute(
                select(nodes).where(nodes.c.id == node_id, nodes.c.project_id == project_id)
            )
            .mappings()
            .first()
        )
        if not row or (active and not row["active"]):
            raise DomainError("Document not found in this project", 404)
        return dict(row)

    def workspace(self, project_id):
        with self.transaction(project_id, write=False) as conn:
            tree = [
                dict(r)
                for r in conn.execute(
                    select(nodes)
                    .where(nodes.c.project_id == project_id, nodes.c.active.is_(True))
                    .order_by(nodes.c.position, nodes.c.id)
                ).mappings()
            ]
            for row in tree:
                row["references"] = json.loads(row.pop("references_json"))
            return {
                "nodes": tree,
                **self.state(conn, project_id),
                "settings": self.effective_settings(conn, project_id),
            }

    def validate_links(self, conn, project_id, node_id, parent_id, references):
        current = parent_id
        visited = {node_id}
        while current:
            if current in visited:
                raise DomainError("Document hierarchy must not contain cycles")
            visited.add(current)
            current = self.node(conn, project_id, current)["parent_id"]
        for reference in references:
            self.node(conn, project_id, reference)

    def create_node(
        self,
        project_id,
        title,
        kind,
        parent_id=None,
        position=0,
        text="",
        original_asset_id=None,
        references=None,
    ):
        validate_text(text)
        node_id = str(uuid4())
        with self.transaction(project_id) as conn:
            count = conn.execute(
                select(func.count()).select_from(nodes).where(nodes.c.project_id == project_id)
            ).scalar_one()
            if count >= 1000:
                raise DomainError("Project limit is 1000 document nodes", 413)
            self.validate_links(conn, project_id, node_id, parent_id, references or [])
            conn.execute(
                nodes.insert().values(
                    id=node_id,
                    project_id=project_id,
                    parent_id=parent_id,
                    title=title,
                    kind=kind,
                    position=position,
                    version=1,
                    active=True,
                    original_asset_id=original_asset_id,
                    references_json=canonical(references or []),
                )
            )
            conn.execute(
                drafts.insert().values(
                    node_id=node_id,
                    project_id=project_id,
                    text=text,
                    version=1,
                    saved_at=timestamp(),
                )
            )
            self.freeze(
                conn, project_id, node_id, "Initial import" if original_asset_id else "Created"
            )
            self.bump(conn, project_id)
        return self.document(project_id, node_id)

    def import_document(self, project_id, filename, stream, title, kind, parent_id, position):
        # Validate before copying to asset storage. If later insertion fails, original asset is retained.
        raw = stream.read(1024 * 1024 + 1)
        text = decode_import(filename, raw)
        stream.seek(0)
        original = self.assets.import_file(project_id, filename, stream)
        return self.create_node(project_id, title, kind, parent_id, position, text, original["id"])

    def edit_node(self, project_id, node_id, version, title, kind, parent_id, position, references):
        with self.transaction(project_id) as conn:
            current = self.node(conn, project_id, node_id)
            if current["version"] != version:
                raise DomainError("Document structure changed; reload before saving", 409)
            self.validate_links(conn, project_id, node_id, parent_id, references)
            conn.execute(
                nodes.update()
                .where(nodes.c.id == node_id)
                .values(
                    title=title,
                    kind=kind,
                    parent_id=parent_id,
                    position=position,
                    references_json=canonical(references),
                    version=version + 1,
                )
            )
            self.bump(conn, project_id)
        return self.document(project_id, node_id)

    def document(self, project_id, node_id):
        with self.transaction(project_id, write=False) as conn:
            row = self.node(conn, project_id, node_id)
            draft = dict(
                conn.execute(select(drafts).where(drafts.c.node_id == node_id)).mappings().one()
            )
            history = [
                dict(r)
                for r in conn.execute(
                    select(
                        revisions.c.id,
                        revisions.c.node_id,
                        revisions.c.project_id,
                        revisions.c.parent_id,
                        revisions.c.restored_from,
                        revisions.c.digest,
                        revisions.c.reason,
                        revisions.c.created_at,
                    )
                    .where(revisions.c.node_id == node_id, revisions.c.project_id == project_id)
                    .order_by(revisions.c.created_at, revisions.c.id)
                ).mappings()
            ]
            row["references"] = json.loads(row.pop("references_json"))
            head = next(r for r in history if r["id"] == row["head_revision_id"])
            return {
                **row,
                "draft": draft,
                "revisions": history,
                "unfrozen": hashlib.sha256(draft["text"].encode()).hexdigest() != head["digest"],
            }

    def save_draft(self, project_id, node_id, version, text):
        validate_text(text)
        with self.transaction(project_id) as conn:
            self.node(conn, project_id, node_id)
            result = conn.execute(
                drafts.update()
                .where(drafts.c.node_id == node_id, drafts.c.version == version)
                .values(text=text, version=version + 1, saved_at=timestamp())
            )
            if result.rowcount != 1:
                raise DomainError(
                    "Draft changed in another editor; your local text is retained. Reload or copy it before resolving.",
                    409,
                )
            self.bump(conn, project_id)
            return dict(
                conn.execute(select(drafts).where(drafts.c.node_id == node_id)).mappings().one()
            )

    def freeze(self, conn, project_id, node_id, reason, *, restored=None):
        node = self.node(conn, project_id, node_id)
        draft = conn.execute(select(drafts).where(drafts.c.node_id == node_id)).mappings().one()
        previous = None
        if node["head_revision_id"]:
            previous = (
                conn.execute(select(revisions).where(revisions.c.id == node["head_revision_id"]))
                .mappings()
                .one()
            )
        digest = self.objects.put(conn, draft["text"])
        if previous and previous["digest"] == digest and not restored:
            return previous["id"]
        units = (
            json.loads(restored["units_json"])
            if restored
            else identify_units(
                json.loads(previous["units_json"]) if previous else [], draft["text"]
            )
        )
        revision_id = str(uuid4())
        conn.execute(
            revisions.insert().values(
                id=revision_id,
                project_id=project_id,
                node_id=node_id,
                parent_id=node["head_revision_id"],
                restored_from=restored["id"] if restored else None,
                digest=digest,
                units_json=canonical(units),
                reason=reason,
                created_at=timestamp(),
            )
        )
        conn.execute(
            nodes.update()
            .where(nodes.c.id == node_id)
            .values(head_revision_id=revision_id, version=node["version"] + 1)
        )
        return revision_id

    def freeze_document(self, project_id, node_id, version, reason):
        with self.transaction(project_id) as conn:
            self.node(conn, project_id, node_id)
            draft = conn.execute(select(drafts).where(drafts.c.node_id == node_id)).mappings().one()
            if draft["version"] != version:
                raise DomainError("Draft changed; reload before freezing", 409)
            revision_id = self.freeze(conn, project_id, node_id, reason)
            self.bump(conn, project_id)
        return {"revision_id": revision_id}

    def revision(self, conn, project_id, node_id, revision_id):
        self.node(conn, project_id, node_id, active=False)
        row = (
            conn.execute(
                select(revisions).where(
                    revisions.c.id == revision_id,
                    revisions.c.node_id == node_id,
                    revisions.c.project_id == project_id,
                )
            )
            .mappings()
            .first()
        )
        if not row:
            raise DomainError("Revision not found in this document", 404)
        return dict(row)

    def revision_detail(self, project_id, node_id, revision_id):
        with self.transaction(project_id, write=False) as conn:
            row = self.revision(conn, project_id, node_id, revision_id)
            return {
                **row,
                "text": self.objects.read(row["digest"]),
                "units": json.loads(row["units_json"]),
            }

    def compare_revision(self, project_id, node_id, revision_id):
        with self.transaction(project_id, write=False) as conn:
            self.node(conn, project_id, node_id)
            revision = self.revision(conn, project_id, node_id, revision_id)
            draft = conn.execute(select(drafts).where(drafts.c.node_id == node_id)).mappings().one()
            return {
                "revision_id": revision_id,
                "draft_version": draft["version"],
                "text_diff": "".join(
                    unified_diff(
                        self.objects.read(revision["digest"]).splitlines(keepends=True),
                        draft["text"].splitlines(keepends=True),
                        fromfile="revision",
                        tofile="current draft",
                    )
                ),
            }

    def restore_document(self, project_id, node_id, revision_id, version):
        with self.transaction(project_id) as conn:
            self.node(conn, project_id, node_id)
            target = self.revision(conn, project_id, node_id, revision_id)
            text = self.objects.read(target["digest"])
            draft = conn.execute(select(drafts).where(drafts.c.node_id == node_id)).mappings().one()
            if draft["version"] != version:
                raise DomainError("Draft changed after preview; reload before restoring", 409)
            self.freeze(conn, project_id, node_id, "Before revision restore")
            conn.execute(
                drafts.update()
                .where(drafts.c.node_id == node_id)
                .values(text=text, version=version + 1, saved_at=timestamp())
            )
            self.freeze(conn, project_id, node_id, "Restored revision", restored=target)
            self.bump(conn, project_id)
        return self.document(project_id, node_id)

    def list_presets(self):
        with self.library.engine.connect() as conn:
            return [
                {**dict(r), "settings": json.loads(r["settings_json"])}
                for r in conn.execute(
                    select(presets).order_by(presets.c.name, presets.c.version)
                ).mappings()
            ]

    def create_preset(self, name, configuration):
        with self.library.engine.begin() as conn:
            conn.exec_driver_sql("BEGIN IMMEDIATE")
            version = (
                conn.execute(
                    select(func.max(presets.c.version)).where(presets.c.name == name)
                ).scalar()
                or 0
            ) + 1
            row = dict(
                id=str(uuid4()),
                name=name,
                version=version,
                settings_json=canonical(configuration),
                created_at=timestamp(),
            )
            conn.execute(presets.insert().values(**row))
            return row

    def effective_settings(self, conn, project_id):
        current = (
            conn.execute(select(settings).where(settings.c.project_id == project_id))
            .mappings()
            .first()
        )
        current = (
            dict(current)
            if current
            else dict(project_id=project_id, version=0, preset_id=None, overrides_json="{}")
        )
        base = {}
        if current["preset_id"]:
            base = json.loads(
                conn.execute(
                    select(presets.c.settings_json).where(presets.c.id == current["preset_id"])
                ).scalar_one()
            )
        overrides = json.loads(current["overrides_json"])
        rules = {(r["term"], r.get("node_id")): r for r in base.get("rules", [])}
        rules.update({(r["term"], r.get("node_id")): r for r in overrides.get("rules", [])})
        resolved = {
            "controls": {**base.get("controls", {}), **overrides.get("controls", {})},
            "rules": list(rules.values()),
        }
        return {**current, "overrides": overrides, "resolved": resolved}

    def write_settings(self, conn, project_id, version, preset_id, overrides):
        current = self.effective_settings(conn, project_id)
        if current["version"] != version:
            raise DomainError("Settings changed; reload before saving", 409)
        if (
            preset_id
            and not conn.execute(select(presets.c.id).where(presets.c.id == preset_id)).first()
        ):
            raise DomainError("Preset version not found", 404)
        for rule in overrides.get("rules", []):
            if rule.get("node_id"):
                self.node(conn, project_id, rule["node_id"])
        data = dict(
            project_id=project_id,
            version=version + 1,
            preset_id=preset_id,
            overrides_json=canonical(overrides),
        )
        conn.execute(settings_history.insert().values(**data, created_at=timestamp()))
        if version:
            conn.execute(
                settings.update().where(settings.c.project_id == project_id).values(**data)
            )
        else:
            conn.execute(settings.insert().values(**data))
        return self.effective_settings(conn, project_id)

    def update_settings(self, project_id, version, preset_id, overrides):
        with self.transaction(project_id) as conn:
            value = self.write_settings(conn, project_id, version, preset_id, overrides)
            self.bump(conn, project_id)
            return value

    def script(self, project_id, node_id, revision_id):
        with self.transaction(project_id, write=False) as conn:
            revision = self.revision(conn, project_id, node_id, revision_id)
            text = self.objects.read(revision["digest"])
            rules = self.effective_settings(conn, project_id)["resolved"]["rules"]
            return {
                "revision_id": revision_id,
                "text": text,
                "anchor_version": 1,
                "units": [
                    {**unit, **resolve_pronunciation(unit["text"], rules, node_id)}
                    for unit in json.loads(revision["units_json"])
                ],
            }

    def manifest(self, conn, project_id, *, freeze=False):
        project = dict(
            conn.execute(select(projects).where(projects.c.id == project_id)).mappings().one()
        )
        tree = []
        total = 0
        for node in (
            conn.execute(
                select(nodes)
                .where(nodes.c.project_id == project_id, nodes.c.active.is_(True))
                .order_by(nodes.c.position, nodes.c.id)
            )
            .mappings()
            .all()
        ):
            if freeze:
                self.freeze(conn, project_id, node["id"], "Project snapshot")
                node = self.node(conn, project_id, node["id"])
            draft = (
                conn.execute(select(drafts).where(drafts.c.node_id == node["id"])).mappings().one()
            )
            total += len(draft["text"].encode("utf-8"))
            if total > 8 * 1024 * 1024:
                raise DomainError(
                    "Phase 2 snapshot/compare limit is 8 MiB of active project text", 413
                )
            # Read every referenced revision to fail safely on missing/corrupt objects.
            revision = self.revision(conn, project_id, node["id"], node["head_revision_id"])
            self.objects.read(revision["digest"])
            tree.append(dict(node) if freeze else {**dict(node), "draft_text": draft["text"]})
        series_context = (
            dict(
                conn.execute(select(series).where(series.c.id == project["series_id"]))
                .mappings()
                .one()
            )
            if project["series_id"]
            else None
        )
        return {
            "format": 1,
            "project": project,
            "series": series_context,
            "nodes": tree,
            "assets": [
                dict(r)
                for r in conn.execute(
                    select(assets, blobs.c.size)
                    .join(blobs)
                    .where(assets.c.project_id == project_id)
                    .order_by(assets.c.id)
                ).mappings()
            ],
            "settings": self.effective_settings(conn, project_id),
        }

    def validate_asset_objects(self, manifest):
        for asset in manifest["assets"]:
            if fingerprint(self.assets.object_path(asset["digest"])) != (
                asset["digest"],
                asset["size"],
            ):
                raise DomainError(
                    "Snapshot references missing/corrupt originals; no restore performed", 409
                )

    def snapshot(self, conn, project_id, name, restored_from=None):
        manifest = self.manifest(conn, project_id, freeze=True)
        self.validate_asset_objects(manifest)
        row = dict(
            id=str(uuid4()),
            project_id=project_id,
            name=name,
            parent_id=self.state(conn, project_id)["head_snapshot_id"],
            restored_from=restored_from,
            manifest_json=canonical(manifest),
            created_at=timestamp(),
        )
        conn.execute(snapshots.insert().values(**row))
        self.bump(conn, project_id, row["id"])
        return row

    def create_snapshot(self, project_id, name, generation, project_version):
        with self.transaction(project_id) as conn:
            self.check_preview(conn, project_id, generation, project_version)
            row = self.snapshot(conn, project_id, name)
            return {"id": row["id"], "name": name}

    def list_snapshots(self, project_id):
        with self.transaction(project_id, write=False) as conn:
            return [
                dict(r)
                for r in conn.execute(
                    select(
                        snapshots.c.id,
                        snapshots.c.name,
                        snapshots.c.parent_id,
                        snapshots.c.restored_from,
                        snapshots.c.created_at,
                    )
                    .where(snapshots.c.project_id == project_id)
                    .order_by(snapshots.c.created_at, snapshots.c.id)
                ).mappings()
            ]

    @staticmethod
    def check_preview(conn, project_id, generation, project_version):
        if (
            Manuscripts.state(conn, project_id)["generation"] != generation
            or conn.execute(
                select(projects.c.version).where(projects.c.id == project_id)
            ).scalar_one()
            != project_version
        ):
            raise DomainError(
                "Project changed after preview; preview again before restoring/snapshotting", 409
            )

    @staticmethod
    def get_snapshot(conn, project_id, snapshot_id):
        row = (
            conn.execute(
                select(snapshots).where(
                    snapshots.c.id == snapshot_id, snapshots.c.project_id == project_id
                )
            )
            .mappings()
            .first()
        )
        if not row:
            raise DomainError("Snapshot not found in this project", 404)
        return dict(row)

    def preview(self, project_id, snapshot_id):
        with self.transaction(project_id, write=False) as conn:
            target = json.loads(self.get_snapshot(conn, project_id, snapshot_id)["manifest_json"])
            for node in target["nodes"]:
                revision = self.revision(conn, project_id, node["id"], node["head_revision_id"])
                node["draft_text"] = self.objects.read(revision["digest"])
            current = self.manifest(conn, project_id)
            old, new = {n["id"]: n for n in current["nodes"]}, {n["id"]: n for n in target["nodes"]}
            changes = []
            for node_id in sorted(old.keys() | new.keys()):
                before, after = old.get(node_id), new.get(node_id)
                fields = (
                    "title",
                    "kind",
                    "parent_id",
                    "position",
                    "references_json",
                    "original_asset_id",
                )
                structure = {
                    k: [before.get(k) if before else None, after.get(k) if after else None]
                    for k in fields
                    if (before or {}).get(k) != (after or {}).get(k)
                }
                diff = "".join(
                    unified_diff(
                        (before or {}).get("draft_text", "").splitlines(keepends=True),
                        (after or {}).get("draft_text", "").splitlines(keepends=True),
                        fromfile="current",
                        tofile="snapshot",
                    )
                )
                if structure or diff or not before or not after:
                    changes.append(
                        {
                            "id": node_id,
                            "title": (after or before)["title"],
                            "structure": structure,
                            "text_diff": diff,
                            "action": "add" if not before else "hide" if not after else "change",
                        }
                    )
            return {
                "snapshot_id": snapshot_id,
                "generation": self.state(conn, project_id)["generation"],
                "project_version": current["project"]["version"],
                "changes": changes,
                "metadata": {"current": current["project"], "target": target["project"]},
                "settings": {"current": current["settings"], "target": target["settings"]},
                "assets": {
                    "current": current["assets"],
                    "target": target["assets"],
                    "policy": "Newer assets are retained; no originals are removed.",
                },
            }

    def restore_snapshot(self, project_id, snapshot_id, generation, project_version):
        with self.transaction(project_id) as conn:
            self.check_preview(conn, project_id, generation, project_version)
            target = json.loads(self.get_snapshot(conn, project_id, snapshot_id)["manifest_json"])
            # Preflight every target object before changing heads. Transaction rollback preserves everything.
            self.validate_asset_objects(target)
            targets = []
            for node in target["nodes"]:
                revision = self.revision(conn, project_id, node["id"], node["head_revision_id"])
                targets.append((node, revision, self.objects.read(revision["digest"])))
            self.snapshot(conn, project_id, "Before snapshot restore")
            conn.execute(
                nodes.update().where(nodes.c.project_id == project_id).values(active=False)
            )
            # Activate all target nodes before validating scoped settings/reference relationships.
            for node, _revision, _text in targets:
                conn.execute(nodes.update().where(nodes.c.id == node["id"]).values(active=True))
            for node, revision, text in targets:
                current = self.node(conn, project_id, node["id"])
                conn.execute(
                    nodes.update()
                    .where(nodes.c.id == node["id"])
                    .values(
                        **{
                            k: node[k]
                            for k in (
                                "title",
                                "kind",
                                "parent_id",
                                "position",
                                "references_json",
                                "original_asset_id",
                            )
                        },
                        version=current["version"] + 1,
                    )
                )
                conn.execute(
                    drafts.update()
                    .where(drafts.c.node_id == node["id"])
                    .values(text=text, version=drafts.c.version + 1, saved_at=timestamp())
                )
                self.freeze(
                    conn, project_id, node["id"], "Restored project snapshot", restored=revision
                )
            # Invalidate stale editor tokens even for hidden documents.
            conn.execute(
                drafts.update()
                .where(
                    drafts.c.project_id == project_id,
                    drafts.c.node_id.not_in([n["id"] for n, _, _ in targets]),
                )
                .values(version=drafts.c.version + 1)
            )
            conn.execute(
                projects.update()
                .where(projects.c.id == project_id)
                .values(
                    **{k: target["project"][k] for k in ("name", "description", "series_id")},
                    version=project_version + 1,
                    updated_at=timestamp(),
                )
            )
            current_settings = self.effective_settings(conn, project_id)
            self.write_settings(
                conn,
                project_id,
                current_settings["version"],
                target["settings"]["preset_id"],
                target["settings"]["overrides"],
            )
            row = self.snapshot(
                conn,
                project_id,
                "Restored: " + self.get_snapshot(conn, project_id, snapshot_id)["name"],
                restored_from=snapshot_id,
            )
            return {"id": row["id"]}
