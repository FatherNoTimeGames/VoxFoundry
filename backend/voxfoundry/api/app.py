import secrets
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.exc import OperationalError
from voxfoundry.application.projects import Projects
from voxfoundry.config import Settings
from voxfoundry.domain.assets import MAX_ASSET_BYTES
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.assets import Assets
from voxfoundry.storage.library import Library, timestamp


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Name(Input):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def printable(cls, value):
        if any(ord(char) < 32 for char in value):
            raise ValueError("Control characters are not allowed")
        return value


class ProjectInput(Name):
    description: str = Field(default="", max_length=10000)
    series_id: UUID | None = None


class EditProject(ProjectInput):
    version: int = Field(ge=1)


class Version(Input):
    version: int = Field(ge=1)


class Bootstrap(Input):
    token: str = Field(min_length=1, max_length=200)


def equal_token(value: str, expected: str) -> bool:
    return secrets.compare_digest(value.encode("utf-8"), expected.encode("utf-8"))


class Security:
    """Host, origin, session/CSRF, request-size and response security boundary."""

    def __init__(self, app, state, port):
        self.app, self.state = app, state
        self.hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if port == 80:
            self.hosts.update({"127.0.0.1", "localhost"})

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope)
        host = request.headers.get("host", "")
        method, path = request.method, request.url.path
        if host not in self.hosts:
            return await JSONResponse({"detail": "Invalid local host"}, 400)(scope, receive, send)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return await JSONResponse({"detail": "Cross-site request rejected"}, 403)(
                scope, receive, send
            )
        origin = request.headers.get("origin")
        if origin is not None and origin != f"http://{host}":
            return await JSONResponse({"detail": "Invalid origin"}, 403)(scope, receive, send)
        api = path.startswith("/api/")
        if api and path not in ("/api/health", "/api/session"):
            if not equal_token(request.cookies.get("vf_session", ""), self.state.session):
                return await JSONResponse({"detail": "Open VoxFoundry using its launcher"}, 401)(
                    scope, receive, send
                )
        if api and method not in ("GET", "HEAD", "OPTIONS"):
            if not origin:
                return await JSONResponse({"detail": "Origin required"}, 403)(scope, receive, send)
            if path != "/api/session" and not equal_token(
                request.headers.get("x-vf-csrf", ""), self.state.csrf
            ):
                return await JSONResponse({"detail": "Invalid session CSRF token"}, 403)(
                    scope, receive, send
                )
        limit = MAX_ASSET_BYTES + 65536
        try:
            length = int(request.headers.get("content-length", "0"))
        except ValueError:
            return await JSONResponse({"detail": "Invalid content length"}, 400)(
                scope, receive, send
            )
        if length > limit:
            return await JSONResponse({"detail": "Upload exceeds 25 MiB asset limit"}, 413)(
                scope, receive, send
            )
        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > limit:
                raise HTTPException(413, "Upload exceeds 25 MiB asset limit")
            return message

        async def secured_send(message):
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"cache-control", b"no-store"),
                    (
                        b"content-security-policy",
                        b"default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
                    ),
                ]
            await send(message)

        await self.app(scope, limited_receive, secured_send)


def create_app(settings: Settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        library = Library(settings.library)
        try:
            app.state.library = library
            app.state.projects = Projects(library)
            app.state.assets = Assets(library, app.state.projects)
            app.state.assets.reconcile()
            yield
        finally:
            library.close()

    app = FastAPI(
        title="VoxFoundry", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
    )
    app.state.bootstrap = secrets.token_urlsafe(32)
    app.state.session = secrets.token_urlsafe(32)
    app.state.csrf = secrets.token_urlsafe(32)
    app.add_middleware(Security, state=app.state, port=settings.port)

    @app.exception_handler(DomainError)
    async def domain_error(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=exc.status)

    @app.exception_handler(OSError)
    async def storage_error(request, exc):
        return JSONResponse({"detail": "Storage I/O failed; check free space and permissions"}, 507)

    @app.exception_handler(OperationalError)
    async def database_error(request, exc):
        return JSONResponse(
            {"detail": "Library storage unavailable; check free space, permissions and locks"}, 503
        )

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.1.0.dev0"}

    @app.post("/api/session")
    async def bootstrap(body: Bootstrap):
        if not app.state.bootstrap or not equal_token(body.token, app.state.bootstrap):
            raise DomainError("Invalid or already used launcher token", 403)
        app.state.bootstrap = None
        response = JSONResponse({"csrf": app.state.csrf})
        response.set_cookie("vf_session", app.state.session, httponly=True, samesite="strict")
        return response

    @app.get("/api/session")
    def session(request: Request):
        if not equal_token(request.cookies.get("vf_session", ""), app.state.session):
            raise DomainError("Open VoxFoundry using its launcher", 401)
        return {"csrf": app.state.csrf}

    @app.get("/api/library")
    def library_info():
        return {
            "id": app.state.library.id,
            "path": str(settings.library),
            "failed_imports": app.state.assets.failed_operations(),
        }

    @app.get("/api/projects")
    def list_projects(trashed: bool = False):
        return app.state.projects.list(trashed)

    @app.post("/api/projects", status_code=201)
    def create_project(body: ProjectInput):
        return app.state.projects.create(
            body.name, body.description, str(body.series_id) if body.series_id else None
        )

    @app.get("/api/projects/{project_id}")
    def get_project(project_id: UUID):
        return app.state.projects.get(str(project_id))

    @app.put("/api/projects/{project_id}")
    def update_project(project_id: UUID, body: EditProject):
        return app.state.projects.update(
            str(project_id),
            body.version,
            name=body.name,
            description=body.description,
            series_id=str(body.series_id) if body.series_id else None,
        )

    @app.post("/api/projects/{project_id}/trash")
    def trash_project(project_id: UUID, body: Version):
        return app.state.projects.update(str(project_id), body.version, trashed_at=timestamp())

    @app.post("/api/projects/{project_id}/restore")
    def restore_project(project_id: UUID, body: Version):
        return app.state.projects.update(str(project_id), body.version, trashed_at=None)

    @app.get("/api/series")
    def list_series():
        return app.state.projects.list_series()

    @app.post("/api/series", status_code=201)
    def create_series(body: Name):
        return app.state.projects.create_series(body.name)

    @app.get("/api/projects/{project_id}/assets")
    def list_assets(project_id: UUID):
        return app.state.assets.list(str(project_id))

    @app.post("/api/projects/{project_id}/assets", status_code=201)
    def upload_asset(project_id: UUID, file: UploadFile):
        try:
            return app.state.assets.import_file(str(project_id), file.filename or "", file.file)
        finally:
            file.file.close()

    @app.get("/api/projects/{project_id}/assets/{asset_id}")
    def download_asset(project_id: UUID, asset_id: UUID):
        path, filename = app.state.assets.download(str(project_id), str(asset_id))
        return FileResponse(
            path,
            media_type="application/octet-stream",
            filename=filename,
            content_disposition_type="attachment",
        )

    if settings.frontend.is_dir():
        app.mount("/assets", StaticFiles(directory=settings.frontend / "assets"), name="ui-assets")

        @app.get("/")
        def index():
            return FileResponse(settings.frontend / "index.html")
    else:

        @app.get("/")
        def missing_ui():
            return JSONResponse(
                {
                    "detail": "Build the UI: npm ci --prefix frontend; npm run build --prefix frontend"
                },
                503,
            )

    return app
