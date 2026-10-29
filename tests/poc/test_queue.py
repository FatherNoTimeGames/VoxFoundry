import hashlib
import json
from uuid import uuid4

import pytest
from voxfoundry.domain.errors import DomainError
from voxfoundry.poc.audio import test_tone as make_tone
from voxfoundry.poc.audio import verify_audio
from voxfoundry.poc.store import Queue


def test_durable_queue_idempotency_and_exclusive_owner(tmp_path):
    root = tmp_path / "bridge"
    queue = Queue(root)
    try:
        request = str(uuid4())
        job = queue.submit(request, "Approved disposable passage")
        assert queue.submit(request, "Approved disposable passage")["id"] == job["id"]
        with pytest.raises(DomainError, match="different text"):
            queue.submit(request, "Different")
        with pytest.raises(ValueError, match="already in use"):
            Queue(root)
    finally:
        queue.close()
    restarted = Queue(root)
    try:
        assert restarted.get(job["id"])["state"] == "queued"
        assert len(restarted.list()) == 1
    finally:
        restarted.close()


def test_leases_fencing_retry_budget_and_explicit_retry(tmp_path):
    clock = [1000.0]
    queue = Queue(tmp_path / "bridge", clock=lambda: clock[0], lease_seconds=10)
    try:
        job = queue.submit(str(uuid4()), "Approved")
        first = queue.claim()
        assert queue.claim() is None
        queue.heartbeat(job["id"], first["lease_token"], 70)
        queue.heartbeat(job["id"], first["lease_token"], 30)
        assert queue.get(job["id"])["progress"] == 70
        clock[0] += 11
        second = queue.claim()
        assert second["attempts"] == 2
        with pytest.raises(DomainError, match="Stale"):
            queue.heartbeat(job["id"], first["lease_token"], 90)
        clock[0] += 11
        assert queue.claim()["attempts"] == 3
        clock[0] += 11
        assert queue.claim() is None
        assert queue.get(job["id"])["state"] == "failed"
        queue.retry(job["id"])
        assert queue.claim()["attempts"] == 4
        with queue.connection() as conn:
            assert conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 4
    finally:
        queue.close()


def test_worker_auth_completion_idempotency_and_durable_audio(tmp_path):
    queue = Queue(tmp_path / "bridge")
    try:
        with pytest.raises(DomainError, match="authentication"):
            queue.authorize("Bearer wrong")
        credential = json.loads((queue.root / "worker-credential.json").read_text())
        queue.authorize("Bearer " + credential["token"])
        assert queue.last_contact()["seconds_since_contact"] is not None
        job = queue.submit(str(uuid4()), "Approved")
        claim = queue.claim()
        content = make_tone(job["text_digest"])
        checksum = verify_audio(content)
        (queue.objects / (checksum + ".wav")).write_bytes(content)
        assert (
            queue.complete(job["id"], claim["lease_token"], checksum, len(content))["state"]
            == "succeeded"
        )
        assert (
            queue.complete(job["id"], claim["lease_token"], checksum, len(content))["state"]
            == "succeeded"
        )
        with pytest.raises(DomainError, match="different bytes"):
            queue.complete(job["id"], claim["lease_token"], "f" * 64, len(content))
        assert queue.claim() is None
    finally:
        queue.close()
    queue = Queue(tmp_path / "bridge")
    try:
        result = queue.get(job["id"])
        assert result["state"] == "succeeded"
        assert (
            hashlib.sha256((queue.objects / (checksum + ".wav")).read_bytes()).hexdigest()
            == checksum
        )
    finally:
        queue.close()


def test_wav_integrity_and_no_model_requirement():
    content = make_tone("a" * 64)
    assert verify_audio(content) == hashlib.sha256(content).hexdigest()
    for invalid in [b"not audio", content[:50], content[:-20]]:
        with pytest.raises(DomainError):
            verify_audio(invalid)


def test_poc_refuses_existing_manuscript_library(tmp_path):
    from voxfoundry.poc.store import private_root

    root = tmp_path / "existing-library"
    root.mkdir()
    original = root / "library.sqlite3"
    original.write_bytes(b"untouched user data")
    with pytest.raises(ValueError, match="separate disposable"):
        private_root(root)
    assert original.read_bytes() == b"untouched user data"
    assert not (root / "queue.sqlite3").exists()
