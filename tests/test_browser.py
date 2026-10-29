"""Real compiled-UI smoke test: no mocked API, persisted data and actual restarts."""

import contextlib
import shutil
import socket
import threading
import time
from urllib.parse import urlencode

import uvicorn
from playwright.sync_api import expect, sync_playwright
from voxfoundry.api.app import create_app
from voxfoundry.config import Settings


@contextlib.contextmanager
def running_app(root):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        app = create_app(Settings(root, port))
        server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level="error"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        deadline = time.monotonic() + 10
        while not server.started:
            if not thread.is_alive() or time.monotonic() >= deadline:
                raise RuntimeError("Test service did not start")
            time.sleep(0.02)
        try:
            yield f"http://127.0.0.1:{port}/#" + urlencode({"token": app.state.bootstrap})
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            assert not thread.is_alive()


def test_compiled_ui_projects_assets_restart_and_tablet(tmp_path):
    library = tmp_path / "library"
    errors, external = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"))
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "request",
            lambda req: (
                external.append(req.url) if not req.url.startswith("http://127.0.0.1:") else None
            ),
        )
        with running_app(library) as url:
            page.goto(url)
            expect(page.get_by_role("button", name="Create project", exact=True)).to_be_visible()
            assert page.evaluate("location.hash") == ""  # launcher token removed from history
            page.get_by_label("New project name").fill("Embervale")
            page.get_by_role("button", name="Create project", exact=True).click()
            expect(page.get_by_role("heading", name="Embervale")).to_be_visible()
            page.get_by_label("Description", exact=True).fill("Documentary project")
            page.get_by_role("button", name="Save changes", exact=True).click()
            expect(page.get_by_role("status")).to_have_text("Project saved.")
            page.get_by_label("Choose original asset").set_input_files(
                {"name": "research.txt", "mimeType": "text/plain", "buffer": b"Original research"}
            )
            page.get_by_role("button", name="Store original").click()
            expect(page.get_by_role("link", name="research.txt")).to_be_visible()
            with page.expect_download() as download:
                page.get_by_role("link", name="research.txt").click()
            assert download.value.suggested_filename == "research.txt"
            assert download.value.path().read_bytes() == b"Original research"
            page.get_by_label("New project name").fill("Independent book")
            page.get_by_role("button", name="Create project", exact=True).click()
            expect(page.get_by_role("heading", name="Independent book")).to_be_visible()
            expect(page.get_by_role("link", name="research.txt")).to_have_count(0)
            page.get_by_role("button", name="Embervale", exact=True).click()
            expect(page.get_by_role("link", name="research.txt")).to_be_visible()
            page.get_by_role("button", name="Move to trash").click()
            page.get_by_role("button", name="Trash", exact=True).click()
            page.get_by_role("button", name="Embervale", exact=True).click()
            expect(page.get_by_role("link", name="research.txt")).to_be_visible()
            page.get_by_role("button", name="Restore project").click()
            page.get_by_role("button", name="Active projects", exact=True).click()
            expect(page.get_by_role("button", name="Embervale", exact=True)).to_be_visible()
        # New service and session: original SQLite + object files only.
        with running_app(library) as url:
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(url)
            page.get_by_role("button", name="Embervale", exact=True).click()
            expect(page.get_by_label("Description", exact=True)).to_have_value(
                "Documentary project"
            )
            expect(page.get_by_role("link", name="research.txt")).to_be_visible()
            expect(page.get_by_role("button", name="Independent book", exact=True)).to_be_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            # Saving metadata must not clear the asset listing for the same project.
            page.get_by_label("Description", exact=True).fill("Revised project description")
            page.get_by_role("button", name="Save changes", exact=True).click()
            expect(page.get_by_role("status")).to_have_text("Project saved.")
            expect(page.get_by_role("link", name="research.txt")).to_be_visible()
        browser.close()
    assert errors == []
    assert external == []
