import argparse
import hashlib
import os
import secrets
import threading
import time
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from voxfoundry.domain.errors import DomainError
from voxfoundry.poc.audio import verify_audio
from voxfoundry.poc.store import MAX_AUDIO, Queue


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Submission(Input):
    request_id: UUID
    text: str = Field(min_length=1, max_length=1000)
    approved: bool = False


class Heartbeat(Input):
    progress: int = Field(ge=0, le=99)


class Bootstrap(Input):
    token: str = Field(min_length=1, max_length=200)


def same(a, b):
    return secrets.compare_digest(a.encode(), b.encode())


class Guard:
    def __init__(self, app, state, port):
        self.app, self.state, self.port = app, state, port

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope)
        host = request.headers.get("host", "")
        if host not in (f"127.0.0.1:{self.port}", f"localhost:{self.port}"):
            return await JSONResponse({"detail": "Invalid loopback host"}, 400)(
                scope, receive, send
            )
        origin = request.headers.get("origin")
        if (origin and origin != f"http://{host}") or request.headers.get(
            "sec-fetch-site"
        ) == "cross-site":
            return await JSONResponse({"detail": "Cross-origin request rejected"}, 403)(
                scope, receive, send
            )
        path, method = request.url.path, request.method
        if path.startswith("/api/") and path not in ("/api/health", "/api/session"):
            if not same(request.cookies.get("vf_poc_session", ""), self.state.session):
                return await JSONResponse({"detail": "Open the POC with its local launcher"}, 401)(
                    scope, receive, send
                )
        if path.startswith("/api/") and method not in ("GET", "HEAD"):
            if not origin or (
                path != "/api/session"
                and not same(request.headers.get("x-vf-csrf", ""), self.state.csrf)
            ):
                return await JSONResponse({"detail": "Owner origin/CSRF check failed"}, 403)(
                    scope, receive, send
                )
        received = 0

        async def bounded_receive():
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > MAX_AUDIO:
                raise DomainError("POC request exceeds 256 KiB", 413)
            return message

        async def secure_send(message):
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + [
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (
                        b"content-security-policy",
                        b"default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'",
                    ),
                ]
            await send(message)

        await self.app(scope, bounded_receive, secure_send)


def create_app(root: Path, port=8766, *, clock=None, lease_seconds=30):
    @asynccontextmanager
    async def lifespan(app):
        app.state.queue = Queue(
            root, **({"clock": clock} if clock else {}), lease_seconds=lease_seconds
        )
        try:
            yield
        finally:
            app.state.queue.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.bootstrap = secrets.token_urlsafe(32)
    app.state.session = secrets.token_urlsafe(32)
    app.state.csrf = secrets.token_urlsafe(32)
    app.add_middleware(Guard, state=app.state, port=port)

    @app.exception_handler(DomainError)
    async def domain_error(request, exc):
        return JSONResponse({"detail": str(exc)}, exc.status)

    @app.exception_handler(OSError)
    async def io_error(request, exc):
        return JSONResponse(
            {"detail": "POC storage unavailable; preserve data and check disk/permissions"}, 507
        )

    @app.get("/api/health")
    def health():
        return {"status": "ok", "implementation": "local POC only; no Sites integration"}

    @app.post("/api/session")
    async def bootstrap(body: Bootstrap):
        if not app.state.bootstrap or not same(body.token, app.state.bootstrap):
            raise DomainError("Invalid/already used launcher token", 403)
        app.state.bootstrap = None
        response = JSONResponse({"csrf": app.state.csrf})
        response.set_cookie("vf_poc_session", app.state.session, httponly=True, samesite="strict")
        return response

    @app.get("/api/session")
    def session(request: Request):
        if not same(request.cookies.get("vf_poc_session", ""), app.state.session):
            raise DomainError("Launch the local POC first", 401)
        return {"csrf": app.state.csrf}

    @app.get("/api/jobs")
    def jobs():
        return app.state.queue.list()

    @app.get("/api/worker-contact")
    def worker_contact():
        return app.state.queue.last_contact()

    @app.post("/api/jobs", status_code=201)
    def submit(body: Submission):
        if (
            not body.approved
            or not body.text.strip()
            or any(ord(c) < 32 and c not in "\n\t" for c in body.text)
        ):
            raise DomainError("Explicitly approve a short printable test passage", 400)
        return app.state.queue.submit(str(body.request_id), body.text)

    @app.post("/api/jobs/{job_id}/retry")
    def retry(job_id: UUID):
        app.state.queue.retry(str(job_id))
        return {"state": "queued"}

    @app.get("/api/jobs/{job_id}/audio")
    def audio(job_id: UUID, download: bool = False):
        job = app.state.queue.get(str(job_id))
        if job["state"] != "succeeded":
            raise DomainError("Audio is not complete", 409)
        path = app.state.queue.objects / (job["audio_digest"] + ".wav")
        if (
            path.is_symlink()
            or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != job["audio_digest"]
        ):
            raise DomainError("Stored audio missing/corrupt; do not release it", 409)
        return FileResponse(
            path,
            media_type="audio/wav",
            filename="voxfoundry-test.wav",
            content_disposition_type="attachment" if download else "inline",
        )

    def worker(request):
        app.state.queue.authorize(request.headers.get("authorization", ""))
        return app.state.queue

    @app.post("/worker/jobs/claim")
    def claim(request: Request):
        return {"job": worker(request).claim()}

    @app.get("/worker/jobs/{job_id}")
    def worker_status(job_id: UUID, request: Request):
        return worker(request).public(app.state.queue.get(str(job_id)))

    @app.post("/worker/jobs/{job_id}/heartbeat")
    def heartbeat(job_id: UUID, body: Heartbeat, request: Request):
        return worker(request).heartbeat(
            str(job_id), request.headers.get("x-lease-token", ""), body.progress
        )

    @app.post("/worker/jobs/{job_id}/fail")
    def failure(job_id: UUID, request: Request):
        worker(request).fail(str(job_id), request.headers.get("x-lease-token", ""))
        return {"state": "failed"}

    @app.post("/worker/jobs/{job_id}/result")
    async def result(job_id: UUID, request: Request):
        queue = worker(request)
        lease = request.headers.get("x-lease-token", "")
        with queue.connection() as conn:
            queue.leased(conn, str(job_id), lease, completed=True)
        stage = queue.staging / str(uuid4())
        try:
            with stage.open("xb") as stream:
                async for chunk in request.stream():
                    stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())
            content = stage.read_bytes()
            audio_digest = verify_audio(content)
            destination = queue.objects / (audio_digest + ".wav")
            if destination.exists() or destination.is_symlink():
                if destination.is_symlink() or destination.read_bytes() != content:
                    raise DomainError("Existing audio object corrupt; refusing overwrite", 409)
            else:
                os.rename(stage, destination)
            completed = queue.complete(str(job_id), lease, audio_digest, len(content))
            if stage.exists():
                stage.unlink()
            return completed
        except BaseException:
            # Partial/orphan objects remain outside all completed job references.
            raise

    ui = Path(__file__).parent

    @app.get("/")
    def index():
        return FileResponse(ui / "poc.html")

    @app.get("/poc.js")
    def javascript():
        return FileResponse(ui / "poc.js", media_type="text/javascript")

    @app.get("/poc.css")
    def stylesheet():
        return FileResponse(ui / "poc.css", media_type="text/css")

    return app


def main():
    parser = argparse.ArgumentParser(
        description="Local Sites/worker protocol experiment, not a deployed Site"
    )
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    app = create_app(args.data, args.port)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=args.port, access_log=False))
    if not args.no_browser:
        url = f"http://127.0.0.1:{args.port}/#" + urlencode({"token": app.state.bootstrap})

        def open_browser():
            while not server.started and not server.should_exit:
                time.sleep(0.1)
            if server.started:
                webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()
    server.run()


if __name__ == "__main__":
    main()
