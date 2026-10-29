import shutil
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from filelock import FileLock, Timeout
from sqlalchemy import URL, create_engine, event, inspect, select
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.schema import libraries

HEAD = "0003"


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def safe_directory(path: Path) -> Path:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise DomainError("Library internal directories must not be links")
    path.mkdir(exist_ok=True)
    if not path.is_dir():
        raise DomainError("Library storage path is not a directory")
    return path


class Library:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        if (self.root / ".instance.lock").is_symlink():
            raise DomainError("Library lock must not be a link")
        self.lock = FileLock(str(self.root / ".instance.lock"))
        self.engine = None
        self.object_lock = threading.RLock()
        try:
            self.lock.acquire(timeout=0)
        except Timeout as exc:
            raise DomainError("Library is already open in another VoxFoundry process", 409) from exc
        try:
            for name in ("objects", "staging", "backups"):
                safe_directory(self.root / name)
            safe_directory(self.root / "objects" / "sha256")
            db = self.root / "library.sqlite3"
            for name in ("library.sqlite3", "library.sqlite3-wal", "library.sqlite3-shm"):
                candidate = self.root / name
                if candidate.is_symlink():
                    raise DomainError("Library database must not be a link")
            self.engine = create_engine(
                URL.create("sqlite", database=str(db)),
                connect_args={"check_same_thread": False, "timeout": 5},
            )

            @event.listens_for(self.engine, "connect")
            def configure(connection, _):
                connection.execute("PRAGMA foreign_keys=ON")
                connection.execute("PRAGMA synchronous=FULL")
                connection.execute("PRAGMA busy_timeout=5000")

            with self.engine.connect() as conn:
                tables = inspect(conn).get_table_names()
                version = (
                    conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar()
                    if "alembic_version" in tables
                    else None
                )
                if tables and version not in ("0001", "0002", HEAD):
                    raise DomainError("Unknown or newer library schema; no changes made")
            if version and version != HEAD:
                if shutil.disk_usage(self.root).free < db.stat().st_size * 2 + 16 * 1024 * 1024:
                    raise DomainError("Insufficient disk space for migration backup")
                backup = self.root / "backups" / f"pre-{HEAD}-{uuid4()}.sqlite3"
                with sqlite3.connect(db) as source, sqlite3.connect(backup) as target:
                    source.backup(target)
                    if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise DomainError("Migration backup failed integrity check")
            cfg = Config()
            cfg.set_main_option("script_location", str(Path(__file__).parent / "migrations"))
            with self.engine.begin() as conn:
                cfg.attributes["connection"] = conn
                command.upgrade(cfg, HEAD)
                if not conn.execute(select(libraries.c.id)).first():
                    conn.execute(libraries.insert().values(id=str(uuid4()), created_at=timestamp()))
            with self.engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL")
                if conn.exec_driver_sql("PRAGMA quick_check").scalar() != "ok":
                    raise DomainError(
                        "Library integrity check failed; preserve it and restore a backup"
                    )
                if conn.exec_driver_sql("PRAGMA foreign_key_check").first():
                    raise DomainError("Library contains invalid relationships")
                self.id = conn.execute(select(libraries.c.id)).scalar_one()
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.engine is not None:
            self.engine.dispose()
        self.lock.release()
