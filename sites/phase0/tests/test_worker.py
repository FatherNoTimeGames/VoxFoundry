"""Protocol-double tests, not hosted Sites/Windows verification."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import urllib.request

SOURCE = Path(__file__).resolve().parents[1] / "worker_client.py"
spec = importlib.util.spec_from_file_location("sites_worker", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProtocolDouble:
    def __init__(self):
        self.pending = True
        self.state = "running"
        self.uploads = 0
        self.lose_ack = False
        self.expire = False
        self.digest = hashlib.sha256(b"Approved test.").hexdigest()

    def request(self, method, path, *, lease="", data=None, audio=None):
        if path.endswith("/claim"):
            if not self.pending:
                return {"job": None}
            self.pending = False
            return {"job": {"id": "job-id", "text": "Approved test.", "text_digest": self.digest,
                            "lease_token": "lease-1", "format": "tone-v1"}}
        if method == "GET":
            return {"state": self.state, "audio_digest": getattr(self, "audio_digest", None)}
        if path.endswith("/result"):
            if self.expire:
                raise module.RemoteError(409)
            self.uploads += 1
            self.audio_digest = module.verify_audio(audio)
            self.state = "succeeded"
            if self.lose_ack:
                self.lose_ack = False
                raise OSError("Simulated dropped acknowledgment")
            return {"state": self.state}
        return {"progress": data["progress"]}


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="voxfoundry-sites-tests-")
        self.root = Path(self.temp.name)
        self.client = ProtocolDouble()

    def tearDown(self):
        self.temp.cleanup()

    def test_original_generator_has_expected_format(self):
        audio = module.test_tone(self.client.digest)
        self.assertEqual(len(audio), 64044)
        self.assertEqual(module.verify_audio(audio), hashlib.sha256(audio).hexdigest())

    def test_render_then_restart_reuses_durable_output(self):
        worker = module.Worker(self.client, self.root)
        self.assertTrue(worker.once(stop_after_render=True))
        self.assertEqual(self.client.uploads, 0)
        restarted = module.Worker(self.client, self.root, renderer=lambda _: self.fail("Duplicate rendering"))
        self.assertTrue(restarted.once())
        self.assertEqual(self.client.uploads, 1)
        self.assertFalse(restarted.once())

    def test_lost_upload_ack_checks_remote_without_rerender(self):
        worker = module.Worker(self.client, self.root)
        self.client.lose_ack = True
        with self.assertRaises(OSError):
            worker.once()
        restarted = module.Worker(self.client, self.root, renderer=lambda _: self.fail("Duplicate rendering"))
        self.assertTrue(restarted.once())
        self.assertEqual(self.client.uploads, 1)

    def test_expired_lease_is_recorded_and_cached_audio_reused_on_reclaim(self):
        worker = module.Worker(self.client, self.root)
        worker.once(stop_after_render=True)
        self.client.expire = True
        self.assertFalse(worker.once())
        self.client.expire = False
        self.client.pending = True
        worker.renderer = lambda _: self.fail("Cache not reused")
        self.assertTrue(worker.once())

    def test_text_digest_mismatch_stops_rendering(self):
        self.client.digest = "0" * 64
        worker = module.Worker(self.client, self.root)
        with self.assertRaises(ValueError):
            worker.once()
        self.assertEqual(self.client.uploads, 0)

    def test_process_lock_excludes_second_worker(self):
        worker = module.Worker(self.client, self.root)
        with sqlite3.connect(worker.db) as db:
            db.execute("BEGIN IMMEDIATE")
            with self.assertRaises(sqlite3.OperationalError):
                worker.once()

    def test_worker_refuses_repository_or_existing_library(self):
        with self.assertRaises(ValueError):
            module.Worker(self.client, module.REPO / "local-data")
        (self.root / "library.sqlite3").touch()
        with self.assertRaises(ValueError):
            module.Worker(self.client, self.root)

    @unittest.skipIf(os.name == "nt", "Windows NTFS ACLs require the real-device manual check")
    def test_existing_shared_cache_directory_is_rejected_before_ledger_creation(self):
        self.root.chmod(0o755)
        try:
            with self.assertRaisesRegex(ValueError, "owner-only"):
                module.Worker(self.client, self.root)
            self.assertFalse((self.root / "sites-worker.sqlite3").exists())
        finally:
            self.root.chmod(0o700)

    def test_transport_has_separate_headers_and_never_follows_redirects(self):
        path = self.root / "worker.credentials.json"
        path.write_text(json.dumps({"site": "https://poc.example", "token": "fake-device",
                                    "service_token": "fake-service"}))
        path.chmod(0o600)
        client = module.Client("https://poc.example", path)
        class Response(io.BytesIO):
            headers = type("Headers", (), {"get_content_type": lambda _: "application/json"})()
        class Opener:
            def open(inner, request, timeout):
                headers = dict(request.header_items())
                self.assertEqual(headers["Oai-sites-authorization"], "Bearer fake-service")
                self.assertEqual(headers["Authorization"], "Bearer fake-device")
                self.assertEqual(timeout, 15)
                return Response(b'{"job":null}')
        client.opener = Opener()
        self.assertEqual(client.request("POST", "/worker/jobs/claim"), {"job": None})
        self.assertIsNone(module.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.example"))
        with self.assertRaises(ValueError):
            client.request("GET", "/api/jobs")

    def test_rejects_insecure_origins_and_mismatched_site(self):
        path = self.root / "worker.credentials.json"
        path.write_text(json.dumps({"site": "https://other.example", "token": "fake", "service_token": "fake"}))
        path.chmod(0o600)
        for origin in ("http://poc.example", "https://poc.example/path", "https://u:p@poc.example", "https://poc.example"):
            with self.assertRaises(ValueError):
                module.Client(origin, path)


if __name__ == "__main__":
    unittest.main()
