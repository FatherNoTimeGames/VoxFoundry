"""Real loopback HTTP/browser evidence; never claims Sites/Windows/Android verification."""

import contextlib
import shutil
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import urlencode
from uuid import uuid4

import httpx
import pytest
import uvicorn
from playwright.sync_api import expect, sync_playwright
from voxfoundry.poc.audio import test_tone as make_tone
from voxfoundry.poc.bridge import create_app
from voxfoundry.poc.worker import Client, Worker


@contextlib.contextmanager
def bridge(root):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        app = create_app(root, port)
        server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level="error"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        deadline = time.monotonic() + 10
        while not server.started:
            assert thread.is_alive() and time.monotonic() < deadline
            time.sleep(0.02)
        origin = f"http://127.0.0.1:{port}"
        try:
            yield app, origin, origin + "/#" + urlencode({"token": app.state.bootstrap})
        finally:
            server.should_exit = True
            thread.join(10)
            assert not thread.is_alive()


@contextlib.contextmanager
def owner(app, origin):
    with httpx.Client(base_url=origin, trust_env=False) as client:
        response = client.post(
            "/api/session", json={"token": app.state.bootstrap}, headers={"Origin": origin}
        )
        assert response.status_code == 200
        client.headers.update({"Origin": origin, "X-VF-CSRF": response.json()["csrf"]})
        yield client


def test_http_auth_limits_fencing_upload_ranges_and_restart(tmp_path):
    root = tmp_path / "bridge"
    with bridge(root) as (app, origin, _), owner(app, origin) as user:
        with httpx.Client(base_url=origin, trust_env=False) as outsider:
            assert outsider.get("/api/jobs").status_code == 401
            assert outsider.post("/worker/jobs/claim").status_code == 401
        data = {
            "request_id": str(uuid4()),
            "text": "Approved disposable request",
            "approved": False,
        }
        assert user.post("/api/jobs", json=data).status_code == 400
        data["approved"] = True
        response = user.post("/api/jobs", json=data)
        assert response.status_code == 201
        job = response.json()
        assert user.post("/api/jobs", json=data).json()["id"] == job["id"]
        remote = Client(origin, root / "worker-credential.json")
        claimed = remote.request("POST", "/worker/jobs/claim")["job"]
        assert (
            user.post("/worker/jobs/" + job["id"] + "/result", content=b"invalid").status_code
            == 401
        )
        headers = {
            "Authorization": "Bearer " + remote.token,
            "X-Lease-Token": claimed["lease_token"],
        }
        assert (
            user.post(
                "/worker/jobs/" + job["id"] + "/result", content=b"bad wav", headers=headers
            ).status_code
            == 400
        )
        assert (
            user.post(
                "/worker/jobs/" + job["id"] + "/result",
                content=b"x" * (256 * 1024 + 1),
                headers=headers,
            ).status_code
            == 413
        )
        audio = make_tone(job["text_digest"])
        assert (
            remote.request(
                "POST",
                "/worker/jobs/" + job["id"] + "/result",
                lease=claimed["lease_token"],
                audio=audio,
            )["state"]
            == "succeeded"
        )
        assert (
            remote.request(
                "POST",
                "/worker/jobs/" + job["id"] + "/result",
                lease=claimed["lease_token"],
                audio=audio,
            )["state"]
            == "succeeded"
        )
        result = user.get("/api/jobs/" + job["id"] + "/audio")
        assert result.content == audio
        assert result.headers["content-type"] == "audio/wav"
        assert (
            user.get(
                "/api/jobs/" + job["id"] + "/audio", headers={"Range": "bytes=0-43"}
            ).status_code
            == 206
        )
        assert (
            user.get("/api/jobs/" + job["id"] + "/audio?download=true")
            .headers["content-disposition"]
            .startswith("attachment;")
        )
        with httpx.Client(base_url=origin, trust_env=False) as outsider:
            assert outsider.get("/api/jobs/" + job["id"] + "/audio").status_code == 401
        assert user.get("/api/jobs", headers={"Host": "evil.invalid"}).status_code == 400
        assert (
            user.post(
                "/api/jobs", json=data, headers={"Origin": "https://evil.invalid"}
            ).status_code
            == 403
        )
    with bridge(root) as (app, origin, _), owner(app, origin) as user:
        assert user.get("/api/jobs").json()[0]["state"] == "succeeded"
        assert user.get("/api/jobs/" + job["id"] + "/audio").content == audio


@pytest.mark.parametrize(
    "viewport,touch",
    [
        ({"width": 390, "height": 844}, True),
        ({"width": 820, "height": 1180}, True),
        ({"width": 1440, "height": 900}, False),
    ],
)
def test_real_worker_subprocess_and_browser_play_download_without_worker(tmp_path, viewport, touch):
    root = tmp_path / "bridge"
    with sync_playwright() as playwright, bridge(root) as (_, origin, url):
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"))
        context = browser.new_context(viewport=viewport, has_touch=touch)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url)
        page.get_by_label("Test passage", exact=True).fill(
            "This passage was approved for a disposable tone test."
        )
        page.get_by_label("I approve this test passage for the disposable audio test.").check()
        page.get_by_role("button", name="Queue test audio", exact=True).click()
        expect(page.locator("#jobs")).to_contain_text("queued")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "voxfoundry.poc.worker",
                "--bridge",
                origin,
                "--credentials",
                str(root / "worker-credential.json"),
                "--data",
                str(tmp_path / "worker"),
            ],
            capture_output=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stderr.decode()
        assert b"Bearer " not in result.stdout + result.stderr
        # Subprocess has exited before playback/download: central stored file remains accessible.
        page.get_by_role("button", name="Refresh jobs", exact=True).click()
        expect(page.locator("#jobs")).to_contain_text("succeeded")
        page.get_by_role("button", name="Play test audio", exact=True).click()
        page.wait_for_function("() => document.querySelector('audio').currentTime > 0.1")
        assert page.locator("audio").evaluate("(audio)=>audio.duration") == 2
        with page.expect_download() as download:
            page.get_by_role("link", name="Download test audio", exact=True).click()
        content = download.value.path().read_bytes()
        assert content.startswith(b"RIFF") and len(content) == 64044
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert page.get_by_role("button", name="Queue test audio").bounding_box()["height"] >= 44
        page.reload()
        expect(page.get_by_role("link", name="Download test audio")).to_be_visible()
        browser.close()
        assert not errors


def test_http_worker_restart_recovers_generated_file_without_regeneration(tmp_path):
    root = tmp_path / "bridge"
    with bridge(root) as (app, origin, _), owner(app, origin) as user:
        response = user.post(
            "/api/jobs", json={"request_id": str(uuid4()), "text": "Approved", "approved": True}
        )
        assert response.status_code == 201
        remote = Client(origin, root / "worker-credential.json")
        worker = Worker(remote, tmp_path / "worker")
        worker.once(stop_after_render=True)

        def no_second_render(checksum):
            raise AssertionError("Should reuse durable generated output")

        assert Worker(remote, tmp_path / "worker", renderer=no_second_render).once()
        assert user.get("/api/jobs").json()[0]["state"] == "succeeded"
