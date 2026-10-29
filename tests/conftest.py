import pytest
from fastapi.testclient import TestClient
from voxfoundry.api.app import create_app
from voxfoundry.config import Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(tmp_path / "library", port=8765)


@pytest.fixture
def client(settings):
    app = create_app(settings)
    with TestClient(app, base_url="http://127.0.0.1:8765") as client:
        response = client.post(
            "/api/session",
            json={"token": app.state.bootstrap},
            headers={"Origin": "http://127.0.0.1:8765"},
        )
        assert response.status_code == 200
        client.headers.update(
            {"Origin": "http://127.0.0.1:8765", "X-VF-CSRF": response.json()["csrf"]}
        )
        yield client
