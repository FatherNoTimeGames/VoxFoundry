import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from voxfoundry.application.projects import Projects
from voxfoundry.config import load_settings
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.library import Library
from voxfoundry.storage.schema import projects


def test_restart_identity_foreign_keys_and_lock(tmp_path):
    root = tmp_path / "library"
    library = Library(root)
    identity = library.id
    service = Projects(library)
    project = service.create("Book", "", None)
    with pytest.raises(DomainError, match="already open"):
        Library(root)
    with library.engine.connect() as conn:
        assert conn.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
        assert conn.exec_driver_sql("PRAGMA journal_mode").scalar() == "wal"
        assert conn.exec_driver_sql("PRAGMA synchronous").scalar() == 2
    library.close()
    reopened = Library(root)
    try:
        assert reopened.id == identity
        assert Projects(reopened).get(project["id"])["name"] == "Book"
    finally:
        reopened.close()


def test_unknown_schema_refuses_without_rewriting(tmp_path):
    root = tmp_path / "library"
    library = Library(root)
    library.close()
    db = root / "library.sqlite3"
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE alembic_version SET version_num='9999'")
    before = db.read_bytes()
    with pytest.raises(DomainError, match="Unknown or newer"):
        Library(root)
    assert db.read_bytes() == before


def test_unversioned_database_refuses(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    with sqlite3.connect(root / "library.sqlite3") as conn:
        conn.execute("CREATE TABLE unrelated (value TEXT)")
    with pytest.raises(DomainError, match="Unknown or newer"):
        Library(root)


def test_migration_preserves_project_and_verified_backup(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    engine = create_engine("sqlite:///" + str(root / "library.sqlite3"))
    cfg = Config()
    cfg.set_main_option(
        "script_location", str(Path("backend/voxfoundry/storage/migrations").resolve())
    )
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "0001")
        conn.execute(
            projects.insert().values(
                id="older-project",
                name="Before upgrade",
                description="",
                version=1,
                created_at="then",
                updated_at="then",
            )
        )
    engine.dispose()
    library = Library(root)
    try:
        assert Projects(library).get("older-project")["name"] == "Before upgrade"
        with library.engine.connect() as conn:
            assert (
                conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar() == "0002"
            )
        (backup,) = (root / "backups").glob("*.sqlite3")
        with sqlite3.connect(backup) as conn:
            assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert conn.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "0001"
            assert conn.execute("SELECT name FROM projects").fetchone()[0] == "Before upgrade"
    finally:
        library.close()


def test_configuration_precedence_and_checkout_rejection(tmp_path, monkeypatch):
    import voxfoundry.config as config

    folder = tmp_path / "config"
    folder.mkdir()
    (folder / "config.json").write_text(
        '{"library":"' + (tmp_path / "configured").as_posix() + '"}'
    )
    monkeypatch.setattr(config, "user_config_path", lambda *a, **k: folder)
    assert load_settings().library == tmp_path / "configured"
    monkeypatch.setenv("VOXFOUNDRY_LIBRARY", str(tmp_path / "environment"))
    assert load_settings().library == tmp_path / "environment"
    assert load_settings(str(tmp_path / "explicit")).library == tmp_path / "explicit"
    with pytest.raises(ValueError, match="outside"):
        load_settings(str(Path.cwd() / "data"))
    with pytest.raises(ValueError, match="absolute"):
        load_settings("relative")


def test_symlink_storage_rejected(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    elsewhere = tmp_path / "outside"
    elsewhere.mkdir()
    try:
        (root / "objects").symlink_to(elsewhere, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation requires additional OS permission")
    with pytest.raises(DomainError, match="links"):
        Library(root)
    assert list(elsewhere.iterdir()) == []


def test_second_process_cannot_open_active_library(tmp_path):
    import subprocess
    import sys

    root = tmp_path / "library"
    library = Library(root)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from pathlib import Path; "
                "from voxfoundry.storage.library import Library; Library(Path(sys.argv[1]))",
                str(root),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert "already open" in result.stderr
    finally:
        library.close()


def test_database_symlink_and_lock_symlink_refused(tmp_path):
    target = tmp_path / "untouched"
    target.write_bytes(b"preserve these bytes")
    for name in ("library.sqlite3", ".instance.lock"):
        root = tmp_path / name.replace(".", "_")
        root.mkdir()
        try:
            (root / name).symlink_to(target)
        except OSError:
            pytest.skip("Symlink creation requires additional OS permission")
        with pytest.raises(DomainError, match="link"):
            Library(root)
        assert target.read_bytes() == b"preserve these bytes"
