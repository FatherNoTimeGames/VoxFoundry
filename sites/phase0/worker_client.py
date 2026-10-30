"""Sites adaptation of backend/voxfoundry/poc/worker.py; standard library only.

Reuses the original audio generator and verifier. Credentials and ledger remain
outside Git. No inbound listener, model, speech API or hosted FFmpeg.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
from voxfoundry.poc.audio import test_tone, verify_audio  # noqa: E402


def private_path(path):
    path = path.expanduser().absolute()
    if path.is_symlink() or path.resolve().is_relative_to(REPO):
        raise ValueError("Keep private worker data outside the repository; no symlinks")
    return path


class RemoteError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__(f"Site returned HTTP {status}; credentials and response omitted")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward either secret to a login redirect or another origin.
        return None


class Client:
    def __init__(self, origin, credentials):
        url = urllib.parse.urlparse(origin)
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.path not in ("", "/") or url.query or url.fragment):
            raise ValueError("Use an HTTPS Site origin without path or credentials")
        path = private_path(credentials)
        if os.name != "nt" and path.stat().st_mode & 0o077:
            raise ValueError("Worker credential file must be owner-only (chmod 600)")
        config = json.loads(path.read_text(encoding="utf-8"))
        self.base = origin.rstrip("/")
        if config.get("site") != self.base:
            raise ValueError("Credential file is bound to a different Site origin")
        self.token = config["token"]
        self.service_token = config["service_token"]
        if not self.token or not self.service_token or any(
            "\n" in value or "\r" in value for value in (self.token, self.service_token)
        ):
            raise ValueError("Both Site and worker credentials are required")
        # Retain inherited HTTPS proxy and TLS trust. Do not log requests/headers.
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, path, *, lease="", data=None, audio=None):
        if not path.startswith("/worker/"):
            raise ValueError("Worker transport is restricted to worker routes")
        headers = {
            "OAI-Sites-Authorization": "Bearer " + self.service_token,
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
        }
        payload = json.dumps(data).encode() if data is not None else None
        if lease:
            headers["X-Lease-Token"] = lease
        if audio is not None:
            payload = audio
            headers["Content-Type"] = "audio/wav"
            headers["X-Audio-SHA256"] = hashlib.sha256(audio).hexdigest()
        request = urllib.request.Request(self.base + path, data=payload, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=15) as response:
                if response.headers.get_content_type() != "application/json":
                    raise ValueError("Expected JSON; private Site boundary not verified")
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise RemoteError(exc.code) from None


class Worker:
    def __init__(self, client, root, renderer=test_tone):
        self.client, self.renderer = client, renderer
        self.root = private_path(root)
        if (self.root / "library.sqlite3").exists():
            raise ValueError("Use fresh disposable worker data, not an existing library")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != "nt":
            info = self.root.stat()
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ValueError("Worker cache directory must be owner-only (chmod 700)")
        if any(p.is_symlink() for p in self.root.iterdir()):
            raise ValueError("Worker data may not contain symlinks")
        self.db = self.root / "sites-worker.sqlite3"
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TABLE IF NOT EXISTS work (id TEXT PRIMARY KEY, digest TEXT NOT NULL, lease TEXT NOT NULL, audio BLOB NOT NULL, state TEXT NOT NULL)")

    def send(self, row):
        state = self.client.request("GET", "/worker/jobs/" + row["id"])
        audio_hash = verify_audio(row["audio"])
        if state["state"] == "succeeded":
            if state["audio_digest"] != audio_hash:
                raise ValueError("Completed remote audio differs; retain local output")
        else:
            self.client.request("POST", "/worker/jobs/" + row["id"] + "/result",
                                lease=row["lease"], audio=row["audio"])

    def once(self, *, stop_after_render=False):
        # A transaction acts as the process lock; no extra lock dependency.
        # Keep rendering durable before upload; never retain the lock across sleeps.
        with sqlite3.connect(self.db, timeout=0) as db:
            db.row_factory = sqlite3.Row
            db.execute("BEGIN IMMEDIATE")
            for row in db.execute("SELECT * FROM work WHERE state='generated'").fetchall():
                try:
                    self.send(row)
                    db.execute("UPDATE work SET state='uploaded' WHERE id=?", (row["id"],))
                    return True
                except RemoteError as exc:
                    if exc.status not in (404, 409):
                        raise
                    db.execute("UPDATE work SET state='lease-lost' WHERE id=?", (row["id"],))
            job = self.client.request("POST", "/worker/jobs/claim")["job"]
            if not job:
                return False
            if (job.get("format") != "tone-v1" or
                    hashlib.sha256(job["text"].encode()).hexdigest() != job["text_digest"]):
                raise ValueError("Unsupported format or text digest mismatch")
            self.client.request("POST", "/worker/jobs/" + job["id"] + "/heartbeat",
                                lease=job["lease_token"], data={"progress": 20})
            cached = db.execute("SELECT audio FROM work WHERE digest=? LIMIT 1", (job["text_digest"],)).fetchone()
            audio = bytes(cached[0]) if cached else self.renderer(job["text_digest"])
            verify_audio(audio)
            row = dict(id=job["id"], digest=job["text_digest"], lease=job["lease_token"], audio=audio)
            db.execute("INSERT INTO work VALUES(:id,:digest,:lease,:audio,'generated') ON CONFLICT(id) DO UPDATE SET lease=excluded.lease,audio=excluded.audio,state='generated'", row)
        # Output survives a crash/lost acknowledgment from this point onward.
        if not stop_after_render:
            # Reacquire the same lock before a network send so another process cannot
            # render concurrently; repeated result uploads are idempotent server-side.
            with sqlite3.connect(self.db, timeout=0) as db:
                db.execute("BEGIN IMMEDIATE")
                self.send(row)
                db.execute("UPDATE work SET state='uploaded' WHERE id=?", (row["id"],))
        return True


def main():
    parser = argparse.ArgumentParser(description="Outbound Sites test-tone worker; no TTS")
    parser.add_argument("--site", required=True)
    parser.add_argument("--credentials", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--poll", action="store_true")
    args = parser.parse_args()
    worker = Worker(Client(args.site, args.credentials), args.data)
    try:
        while True:
            worked = worker.once()
            print("Test job handled." if worked else "No claimable job.")
            if not args.poll:
                break
            # 15 seconds bounds D1 polling traffic; Ctrl+C remains responsive.
            time.sleep(15)
    except KeyboardInterrupt:
        pass
    except (RemoteError, ValueError, OSError, sqlite3.Error):
        # Avoid tracebacks containing paths, HTTP bodies or credential material.
        print("Worker stopped. Check private access, enrollment and retained job state.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
