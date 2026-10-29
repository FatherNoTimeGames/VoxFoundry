import errno
import hashlib
from io import BytesIO
from uuid import uuid4

import pytest
from sqlalchemy import select
from voxfoundry.application.projects import Projects
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.assets import Assets
from voxfoundry.storage.library import Library, timestamp
from voxfoundry.storage.schema import operations


@pytest.fixture
def store(tmp_path):
    library = Library(tmp_path / "library")
    projects = Projects(library)
    project = projects.create("Book", "", None)
    assets = Assets(library, projects)
    yield assets, project["id"]
    library.close()


def test_interrupted_ready_publication_recovers_and_partial_remains(store):
    store, project_id = store
    content = b"Original source"
    digest = hashlib.sha256(content).hexdigest()
    ready = dict(
        id=str(uuid4()),
        project_id=project_id,
        asset_id=str(uuid4()),
        filename="source.txt",
        state="ready",
        digest=digest,
        size=len(content),
        created_at=timestamp(),
    )
    partial = dict(
        id=str(uuid4()),
        project_id=project_id,
        asset_id=str(uuid4()),
        filename="partial.txt",
        state="writing",
        created_at=timestamp(),
    )
    with store.library.engine.begin() as conn:
        conn.execute(operations.insert().values(**ready))
        conn.execute(operations.insert().values(**partial))
    store._stage(ready["id"]).write_bytes(content)
    store._stage(partial["id"]).write_bytes(b"incomplete")
    store.reconcile()
    assert store.get(project_id, ready["asset_id"])["state"] == "valid"
    assert store.download(project_id, ready["asset_id"])[0].read_bytes() == content
    assert store._stage(partial["id"]).read_bytes() == b"incomplete"
    assert len(store.failed_operations()) == 1
    store.reconcile()
    assert len(store.list(project_id)) == 1  # recovery idempotency


def test_crash_after_publish_before_database_commit(store, monkeypatch):
    store, project_id = store
    original_record = store._record

    def crash(op):
        raise RuntimeError("simulated process death")

    monkeypatch.setattr(store, "_record", crash)
    with pytest.raises(RuntimeError):
        store.import_file(project_id, "original.txt", BytesIO(b"original"))
    assert store.list(project_id) == []
    monkeypatch.setattr(store, "_record", original_record)
    store.reconcile()
    assert len(store.list(project_id)) == 1
    assert store.list(project_id)[0]["state"] == "valid"


def test_disk_full_partial_write_keeps_journal_and_original(store):
    store, project_id = store

    class DiskFull(BytesIO):
        def read(self, size):
            if self.tell():
                raise OSError(errno.ENOSPC, "disk full")
            return super().read(3)

    original = DiskFull(b"original manuscript")
    with pytest.raises(DomainError, match="free space"):
        store.import_file(project_id, "source.txt", original)
    assert original.getvalue() == b"original manuscript"
    assert store.list(project_id) == []
    assert store.failed_operations()[0]["state"] == "failed"
    assert next((store.library.root / "staging").iterdir()).read_bytes() == b"ori"


def test_corrupt_missing_and_no_overwrite(store):
    store, project_id = store
    asset = store.import_file(project_id, "source.txt", BytesIO(b"original"))
    path = store.object_path(asset["digest"])
    path.write_bytes(b"corrupt")  # external damage, not app editing
    store.reconcile()
    assert store.get(project_id, asset["id"])["state"] == "corrupt"
    with pytest.raises(DomainError, match="corrupt"):
        store.download(project_id, asset["id"])
    with pytest.raises(DomainError, match="corrupt"):
        store.import_file(project_id, "again.txt", BytesIO(b"original"))
    assert path.read_bytes() == b"corrupt"
    path.unlink()
    store.reconcile()
    assert store.get(project_id, asset["id"])["state"] == "missing"


def test_write_fsync_failure_no_successful_reference(store, monkeypatch):
    import voxfoundry.storage.assets as module

    store, project_id = store

    def fail(fd):
        raise OSError(errno.ENOSPC, "disk full")

    monkeypatch.setattr(module.os, "fsync", fail)
    with pytest.raises(DomainError):
        store.import_file(project_id, "original.txt", BytesIO(b"preserved"))
    assert store.list(project_id) == []
    with store.library.engine.connect() as conn:
        assert conn.execute(select(operations.c.state)).scalar() == "failed"


def test_concurrent_identical_uploads_deduplicate_without_lost_references(store):
    from concurrent.futures import ThreadPoolExecutor

    store, project_id = store
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda i: store.import_file(project_id, f"{i}.txt", BytesIO(b"same")), range(2)
            )
        )
    assert len({r["id"] for r in results}) == 2
    assert len({r["digest"] for r in results}) == 1
    assert len(store.list(project_id)) == 2
    assert len(list(store.library.root.glob("objects/sha256/*/*"))) == 1
