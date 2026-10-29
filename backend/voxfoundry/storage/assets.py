import hashlib
import os
import re
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from voxfoundry.domain.assets import MAX_ASSET_BYTES, validate_filename
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.library import safe_directory, timestamp
from voxfoundry.storage.schema import assets, blobs, operations


def fingerprint(path: Path) -> tuple[str, int]:
    if path.is_symlink() or not path.is_file():
        raise DomainError("Asset missing or unsafe; original reference retained", 409)
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest(), path.stat().st_size


def flush_directory(path: Path):
    # Windows has no portable directory fsync; target-platform power-loss testing remains a gate.
    if os.name != "nt":
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


class Assets:
    def __init__(self, library, project_service):
        self.library = library
        self.projects = project_service
        self.publish_lock = library.object_lock

    def object_path(self, digest):
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise DomainError("Invalid object digest", 409)
        base = safe_directory(self.library.root / "objects")
        base = safe_directory(base / "sha256")
        bucket = safe_directory(base / digest[:2])
        return bucket / digest

    def _stage(self, operation_id):
        if not re.fullmatch(r"[0-9a-f-]{36}", operation_id):
            raise DomainError("Invalid operation identifier", 409)
        folder = safe_directory(self.library.root / "staging")
        return folder / operation_id

    def _record(self, op):
        path = self.object_path(op["digest"])
        if fingerprint(path) != (op["digest"], op["size"]):
            raise DomainError(
                "Object integrity mismatch; refusing to overwrite existing bytes", 409
            )
        with self.library.engine.begin() as conn:
            conn.exec_driver_sql("BEGIN IMMEDIATE")
            existing = conn.execute(select(blobs).where(blobs.c.digest == op["digest"])).first()
            if not existing:
                conn.execute(
                    blobs.insert().values(digest=op["digest"], size=op["size"], state="valid")
                )
            else:
                conn.execute(
                    blobs.update().where(blobs.c.digest == op["digest"]).values(state="valid")
                )
            if not conn.execute(select(assets.c.id).where(assets.c.id == op["asset_id"])).first():
                conn.execute(
                    assets.insert().values(
                        id=op["asset_id"],
                        project_id=op["project_id"],
                        digest=op["digest"],
                        filename=op["filename"],
                        created_at=op["created_at"],
                    )
                )
            conn.execute(
                operations.update()
                .where(operations.c.id == op["id"])
                .values(state="succeeded", error=None)
            )

    def _publish(self, op):
        with self.publish_lock:
            self._publish_locked(op)
        # Never wait for SQLite while holding the object lock: revision transactions
        # acquire the database first, then publish text objects.
        self._record(op)
        stage = self._stage(op["id"])
        if stage.exists():
            try:
                stage.unlink()
            except OSError:
                pass  # committed asset is valid; retain the harmless staging copy

    def _publish_locked(self, op):
        stage = self._stage(op["id"])
        destination = self.object_path(op["digest"])
        if destination.exists() or destination.is_symlink():
            # Never overwrite: corruption must be resolved explicitly, not hidden by a new upload.
            if fingerprint(destination) != (op["digest"], op["size"]):
                raise DomainError("Existing object is corrupt; original bytes retained", 409)
        else:
            if fingerprint(stage) != (op["digest"], op["size"]):
                raise DomainError("Staged asset integrity mismatch", 409)
            os.rename(stage, destination)
            flush_directory(destination.parent)

    def import_file(self, project_id, filename, stream):
        self.projects.get(project_id, active=True)
        validate_filename(filename)
        op = dict(
            id=str(uuid4()),
            project_id=project_id,
            asset_id=str(uuid4()),
            filename=filename,
            state="writing",
            created_at=timestamp(),
        )
        with self.library.engine.begin() as conn:
            conn.execute(operations.insert().values(**op))
        try:
            digest = hashlib.sha256()
            size = 0
            with self._stage(op["id"]).open("xb") as target:
                while chunk := stream.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_ASSET_BYTES:
                        raise DomainError("Phase 1 asset limit is 25 MiB", 413)
                    target.write(chunk)
                    digest.update(chunk)
                target.flush()
                os.fsync(target.fileno())
            op.update(digest=digest.hexdigest(), size=size, state="ready")
            with self.library.engine.begin() as conn:
                conn.execute(
                    operations.update()
                    .where(operations.c.id == op["id"])
                    .values(digest=op["digest"], size=size, state="ready")
                )
            self._publish(op)
        except (OSError, DomainError) as exc:
            message = (
                str(exc)
                if isinstance(exc, DomainError)
                else "Asset I/O failed; check free space and permissions"
            )
            with self.library.engine.begin() as conn:
                conn.execute(
                    operations.update()
                    .where(operations.c.id == op["id"])
                    .values(state="failed", error=message)
                )
            if isinstance(exc, DomainError):
                raise
            raise DomainError(message, 507) from exc
        return self.get(project_id, op["asset_id"])

    def list(self, project_id):
        self.projects.get(project_id)
        with self.library.engine.connect() as conn:
            return [
                dict(r)
                for r in conn.execute(
                    select(assets, blobs.c.size, blobs.c.state)
                    .join(blobs)
                    .where(assets.c.project_id == project_id)
                    .order_by(assets.c.created_at, assets.c.id)
                ).mappings()
            ]

    def get(self, project_id, asset_id):
        for asset in self.list(project_id):
            if asset["id"] == asset_id:
                return asset
        raise DomainError("Asset not found in this project", 404)

    def download(self, project_id, asset_id):
        asset = self.get(project_id, asset_id)
        path = self.object_path(asset["digest"])
        try:
            if fingerprint(path) != (asset["digest"], asset["size"]):
                raise DomainError("Asset is corrupt; original reference retained", 409)
        except (OSError, DomainError) as exc:
            with self.library.engine.begin() as conn:
                conn.execute(
                    blobs.update()
                    .where(blobs.c.digest == asset["digest"])
                    .values(state="corrupt" if path.exists() else "missing")
                )
            raise DomainError("Asset missing or corrupt; original reference retained", 409) from exc
        return path, asset["filename"]

    def reconcile(self):
        with self.library.engine.connect() as conn:
            pending = [
                dict(r)
                for r in conn.execute(
                    select(operations).where(operations.c.state.in_(["writing", "ready"]))
                ).mappings()
            ]
        for op in pending:
            try:
                if op["state"] != "ready":
                    raise DomainError(
                        "Interrupted upload; partial staging retained. Upload the original again."
                    )
                self._publish(op)
            except (OSError, DomainError) as exc:
                with self.library.engine.begin() as conn:
                    conn.execute(
                        operations.update()
                        .where(operations.c.id == op["id"])
                        .values(
                            state="failed",
                            error=str(exc)
                            if isinstance(exc, DomainError)
                            else "Recovery I/O failed; staging retained",
                        )
                    )
        with self.library.engine.connect() as conn:
            stored = [dict(r) for r in conn.execute(select(blobs)).mappings()]
        for blob in stored:
            try:
                path = self.object_path(blob["digest"])
                state = (
                    "valid" if fingerprint(path) == (blob["digest"], blob["size"]) else "corrupt"
                )
            except (OSError, DomainError):
                state = "missing"
            with self.library.engine.begin() as conn:
                conn.execute(
                    blobs.update().where(blobs.c.digest == blob["digest"]).values(state=state)
                )

    def failed_operations(self):
        with self.library.engine.connect() as conn:
            return [
                dict(r)
                for r in conn.execute(
                    select(operations).where(operations.c.state == "failed")
                ).mappings()
            ]
