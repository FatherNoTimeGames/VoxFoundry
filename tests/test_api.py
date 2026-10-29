from uuid import uuid4

from fastapi.testclient import TestClient
from voxfoundry.api.app import create_app


def create(client, name="Book", **kwargs):
    response = client.post("/api/projects", json={"name": name, **kwargs})
    assert response.status_code == 201, response.text
    return response.json()


def test_crud_series_conflicts_trash_and_isolation(client):
    series = client.post("/api/series", json={"name": "Documentaries"}).json()
    a = create(client, "Embervale", series_id=series["id"])
    b = create(client, "Independent")
    assert a["id"] != b["id"]
    assert client.get("/api/series").json()[0]["id"] == series["id"]
    saved = client.put(
        "/api/projects/" + a["id"],
        json={
            "name": "Updated",
            "description": "Research",
            "version": 1,
            "series_id": series["id"],
        },
    )
    assert saved.status_code == 200
    assert saved.json()["version"] == 2
    assert (
        client.put("/api/projects/" + a["id"], json={"name": "Stale", "version": 1}).status_code
        == 409
    )
    assert client.get("/api/projects/" + b["id"]).json()["name"] == "Independent"
    assert client.post(f"/api/projects/{a['id']}/trash", json={"version": 2}).status_code == 200
    assert [p["id"] for p in client.get("/api/projects").json()] == [b["id"]]
    assert client.get("/api/projects?trashed=true").json()[0]["id"] == a["id"]
    assert client.post(f"/api/projects/{a['id']}/restore", json={"version": 3}).status_code == 200
    assert len(client.get("/api/projects").json()) == 2
    assert client.delete("/api/projects/" + a["id"]).status_code == 405


def test_input_validation(client):
    for name in ("", "   ", "x" * 201, "bad\x00name"):
        assert client.post("/api/projects", json={"name": name}).status_code == 422
    assert client.post("/api/projects", json={"name": "Valid", "surprise": 1}).status_code == 422
    assert (
        client.post("/api/projects", json={"name": "Valid", "series_id": str(uuid4())}).status_code
        == 404
    )
    assert client.get("/api/projects/not-a-uuid").status_code == 422
    assert client.get("/api/projects/" + str(uuid4())).status_code == 404


def test_session_bootstrap_security_and_headers(settings):
    app = create_app(settings)
    with TestClient(app, base_url="http://127.0.0.1:8765") as client:
        assert client.get("/api/health").json()["status"] == "ok"
        assert client.get("/api/projects").status_code == 401
        assert client.get("/api/library", headers={"Host": "evil.invalid:8765"}).status_code == 400
        assert client.get("/api/library", headers={"Host": "127.0.0.1:1234"}).status_code == 400
        assert client.post("/api/session", json={"token": app.state.bootstrap}).status_code == 403
        origin = {"Origin": "http://127.0.0.1:8765"}
        token = app.state.bootstrap
        assert (
            client.post(
                "/api/session", json={"token": token}, headers={"Origin": "https://evil.invalid"}
            ).status_code
            == 403
        )
        response = client.post("/api/session", json={"token": token}, headers=origin)
        assert response.status_code == 200
        assert "httponly" in response.headers["set-cookie"].lower()
        assert "samesite=strict" in response.headers["set-cookie"].lower()
        assert client.post("/api/session", json={"token": token}, headers=origin).status_code == 403
        assert client.get("/api/projects").status_code == 200
        assert (
            client.post("/api/projects", json={"name": "CSRF"}, headers=origin).status_code == 403
        )
        assert client.get("/api/projects", headers={"Origin": "null"}).status_code == 403
        assert (
            client.get("/api/projects", headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403
        )
        assert "frame-ancestors" in client.get("/api/projects").headers["content-security-policy"]
        assert client.get("/api/projects").headers["cache-control"] == "no-store"


def test_asset_scoping_dedup_attachment_and_trash(client):
    a, b = create(client, "A"), create(client, "B")
    data = b"<script>must never execute</script>"

    def upload(project):
        return client.post(
            f"/api/projects/{project['id']}/assets",
            files={"file": ("research.html", data, "text/html")},
        )

    first, second = upload(a), upload(b)
    assert first.status_code == second.status_code == 201
    first, second = first.json(), second.json()
    assert first["digest"] == second["digest"]
    assert first["id"] != second["id"]
    path = f"/api/projects/{a['id']}/assets/{first['id']}"
    assert client.get(f"/api/projects/{b['id']}/assets/{first['id']}").status_code == 404
    download = client.get(path)
    assert download.content == data
    assert download.headers["content-type"] == "application/octet-stream"
    assert download.headers["content-disposition"].startswith("attachment;")
    assert len(list(client.app.state.library.root.glob("objects/sha256/*/*"))) == 1
    client.post(f"/api/projects/{a['id']}/trash", json={"version": 1})
    assert upload(a).status_code == 404
    assert client.get(path).content == data


def test_asset_path_validation_and_size_limit(client):
    project = create(client)
    for name in ("../escape", "CON.txt", "trailing.", "bad:name", "x/y"):
        assert (
            client.post(
                f"/api/projects/{project['id']}/assets", files={"file": (name, b"no")}
            ).status_code
            == 400
        )
    assert (
        client.post(
            f"/api/projects/{project['id']}/assets",
            content=b"",
            headers={"Content-Length": str(26 * 1024 * 1024)},
        ).status_code
        == 413
    )


def test_chunked_upload_limit(client, monkeypatch):
    # No Content-Length: enforce the ASGI stream bound as well as declared length.
    import voxfoundry.api.app as module

    monkeypatch.setattr(module, "MAX_ASSET_BYTES", 1)
    project = create(client)

    def chunks():
        yield b'--boundary\r\nContent-Disposition: form-data; name="file"; filename="test.txt"\r\n\r\n'
        yield b"x" * 70000
        yield b"\r\n--boundary--\r\n"

    response = client.post(
        f"/api/projects/{project['id']}/assets",
        content=chunks(),
        headers={"Content-Type": "multipart/form-data; boundary=boundary"},
    )
    assert response.status_code == 413


def test_windows_multipart_filename_is_basename_and_domain_rejects_paths(client):
    import pytest
    from voxfoundry.domain.assets import validate_filename
    from voxfoundry.domain.errors import DomainError

    with pytest.raises(DomainError):
        validate_filename("C:\\private.txt")
    project = create(client)
    # Multipart parsers normalize browser-supplied Windows paths to the basename.
    response = client.post(
        f"/api/projects/{project['id']}/assets",
        files={"file": ("C:\\private.txt", b"safe original")},
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "private.txt"


def test_concurrent_metadata_edits_have_one_winner(client):
    from concurrent.futures import ThreadPoolExecutor

    project = create(client)

    def edit(name):
        return client.put("/api/projects/" + project["id"], json={"name": name, "version": 1})

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(edit, ["First writer", "Second writer"]))
    assert sorted(r.status_code for r in results) == [200, 409]
    saved = client.get("/api/projects/" + project["id"]).json()
    winner = next(r.json() for r in results if r.status_code == 200)
    assert saved["name"] == winner["name"]
    assert saved["version"] == 2


def test_non_ascii_auth_input_is_rejected_not_server_error(settings):
    app = create_app(settings)
    with TestClient(app, base_url="http://127.0.0.1:8765") as client:
        assert (
            client.post(
                "/api/session",
                json={"token": "not-a-token-\u00e9"},
                headers={"Origin": "http://127.0.0.1:8765"},
            ).status_code
            == 403
        )
