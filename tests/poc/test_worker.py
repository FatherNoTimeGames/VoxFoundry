from uuid import uuid4

from voxfoundry.domain.errors import DomainError
from voxfoundry.poc.audio import test_tone as make_tone
from voxfoundry.poc.audio import verify_audio
from voxfoundry.poc.store import Queue
from voxfoundry.poc.worker import RemoteError, Worker


class DirectProtocol:
    """State-machine contract double, not evidence of HTTP/Sites/Windows integration."""

    def __init__(self, queue):
        self.queue = queue

    def request(self, method, path, lease="", data=None, audio=None):
        if path == "/worker/jobs/claim":
            return {"job": self.queue.claim()}
        job_id = path.split("/")[3]
        if method == "GET":
            return self.queue.public(self.queue.get(job_id))
        if path.endswith("/heartbeat"):
            return self.queue.heartbeat(job_id, lease, data["progress"])
        if path.endswith("/result"):
            try:
                checksum = verify_audio(audio)
                (self.queue.objects / (checksum + ".wav")).write_bytes(audio)
                return self.queue.complete(job_id, lease, checksum, len(audio))
            except DomainError as exc:
                raise RemoteError(exc.status) from exc
        raise AssertionError("Unknown protocol operation")


def test_worker_restart_reuses_generated_output_after_disconnect(tmp_path):
    queue = Queue(tmp_path / "bridge")
    try:
        job = queue.submit(str(uuid4()), "Approved")
        renders = []

        def render(checksum):
            renders.append(checksum)
            return make_tone(checksum)

        worker = Worker(DirectProtocol(queue), tmp_path / "worker", renderer=render)
        assert worker.once(stop_after_render=True)
        assert queue.get(job["id"])["state"] == "leased"
        del worker
        restarted = Worker(DirectProtocol(queue), tmp_path / "worker", renderer=render)
        assert restarted.once()
        assert queue.get(job["id"])["state"] == "succeeded"
        assert restarted.once() is False
        assert len(renders) == 1
    finally:
        queue.close()


def test_expired_lease_reclaims_and_reuses_audio_cache(tmp_path):
    clock = [100.0]
    queue = Queue(tmp_path / "bridge", clock=lambda: clock[0], lease_seconds=10)
    try:
        job = queue.submit(str(uuid4()), "Approved")
        renders = []

        def render(checksum):
            renders.append(checksum)
            return make_tone(checksum)

        worker = Worker(DirectProtocol(queue), tmp_path / "worker", renderer=render)
        worker.once(stop_after_render=True)
        clock[0] += 11
        assert Worker(DirectProtocol(queue), tmp_path / "worker", renderer=render).once()
        assert queue.get(job["id"])["state"] == "succeeded"
        assert queue.get(job["id"])["attempts"] == 2
        assert len(renders) == 1
    finally:
        queue.close()
