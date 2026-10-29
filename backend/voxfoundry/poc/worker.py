"""Outbound-only portable harness; Windows execution is a separate manual gate."""

import argparse
import hashlib
import json
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from filelock import FileLock

from voxfoundry.poc.audio import test_tone, verify_audio
from voxfoundry.poc.store import private_root


class RemoteError(Exception):
    def __init__(self, status):
        super().__init__(
            f"Bridge returned HTTP {status}; inspect job status without logging credentials"
        )
        self.status = status


class Client:
    def __init__(self, base_url: str, credential_path: Path):
        url = urllib.parse.urlparse(base_url)
        if url.username or url.password or url.query or url.fragment or url.path not in ("", "/"):
            raise ValueError("Use a bridge origin without credentials, path or query")
        if url.scheme != "https" and not (
            url.scheme == "http" and url.hostname in ("127.0.0.1", "localhost")
        ):
            raise ValueError("HTTPS required outside loopback")
        self.base = base_url.rstrip("/")
        self.token = json.loads(credential_path.read_text(encoding="utf-8"))["token"]
        # Direct local sockets only for loopback. External destinations retain inherited proxy/TLS trust.
        self.opener = (
            urllib.request.build_opener(urllib.request.ProxyHandler({}))
            if url.hostname in ("127.0.0.1", "localhost")
            else urllib.request.build_opener()
        )

    def request(self, method, path, *, lease="", data=None, audio=None):
        headers = {"Authorization": "Bearer " + self.token, "Content-Type": "application/json"}
        if lease:
            headers["X-Lease-Token"] = lease
        body = json.dumps(data).encode() if data is not None else None
        if audio is not None:
            body = audio
            headers["Content-Type"] = "audio/wav"
        request = urllib.request.Request(
            self.base + path, data=body, headers=headers, method=method
        )
        try:
            with self.opener.open(request, timeout=10) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise RemoteError(exc.code) from None


class Worker:
    def __init__(self, client, root: Path, renderer=test_tone):
        self.client = client
        self.root = private_root(root)
        self.renderer = renderer
        self.db = self.root / "worker.sqlite3"
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS work (id TEXT PRIMARY KEY, text_digest TEXT NOT NULL, lease TEXT NOT NULL, state TEXT NOT NULL, path TEXT NOT NULL, audio_digest TEXT NOT NULL)"
            )
        self.lock = FileLock(str(self.root / ".worker.lock"))

    def send(self, row):
        job = self.client.request("GET", "/worker/jobs/" + row["id"])
        if job["state"] == "succeeded":
            if job["audio_digest"] != row["audio_digest"]:
                raise ValueError("Completed remote audio differs from local output; retain both")
        else:
            path = Path(row["path"])
            if path.is_symlink() or not path.resolve().is_relative_to(self.root.resolve()):
                raise ValueError("Worker cache path escaped its private data directory")
            content = path.read_bytes()
            if verify_audio(content) != row["audio_digest"]:
                raise ValueError("Local cached test audio is corrupt")
            self.client.request(
                "POST", "/worker/jobs/" + row["id"] + "/result", lease=row["lease"], audio=content
            )
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE work SET state='uploaded' WHERE id=?", (row["id"],))

    def once(self, *, stop_after_render=False):
        with self.lock.acquire(timeout=0):
            with sqlite3.connect(self.db) as conn:
                conn.row_factory = sqlite3.Row
                pending = [
                    dict(r) for r in conn.execute("SELECT * FROM work WHERE state='generated'")
                ]
            for row in pending:
                try:
                    self.send(row)
                    return True
                except RemoteError as exc:
                    if exc.status != 409:
                        raise
                    with sqlite3.connect(self.db) as conn:
                        conn.execute("UPDATE work SET state='lease-lost' WHERE id=?", (row["id"],))
            job = self.client.request("POST", "/worker/jobs/claim")["job"]
            if not job:
                return False
            if hashlib.sha256(job["text"].encode()).hexdigest() != job["text_digest"]:
                raise ValueError("Job text digest mismatch; do not generate")
            self.client.request(
                "POST",
                "/worker/jobs/" + job["id"] + "/heartbeat",
                lease=job["lease_token"],
                data={"progress": 20},
            )
            cached = self.root / (job["text_digest"] + ".wav")
            if cached.is_symlink():
                raise ValueError("Worker cache must not be a symlink")
            if not cached.exists():
                content = self.renderer(job["text_digest"])
                verify_audio(content)
                temporary = self.root / (job["id"] + ".staging")
                with temporary.open("xb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.rename(temporary, cached)
            audio_digest = verify_audio(cached.read_bytes())
            row = dict(
                id=job["id"],
                text_digest=job["text_digest"],
                lease=job["lease_token"],
                state="generated",
                path=str(cached),
                audio_digest=audio_digest,
            )
            with sqlite3.connect(self.db) as conn:
                conn.execute(
                    "INSERT INTO work VALUES(:id,:text_digest,:lease,:state,:path,:audio_digest) ON CONFLICT(id) DO UPDATE SET lease=excluded.lease,state=excluded.state,path=excluded.path,audio_digest=excluded.audio_digest",
                    row,
                )
            self.client.request(
                "POST",
                "/worker/jobs/" + job["id"] + "/heartbeat",
                lease=job["lease_token"],
                data={"progress": 80},
            )
            if not stop_after_render:
                self.send(row)
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Portable test-tone worker; no TTS models or inbound ports"
    )
    parser.add_argument("--bridge", default="http://127.0.0.1:8766")
    parser.add_argument("--credentials", required=True, type=Path)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--poll", action="store_true")
    args = parser.parse_args()
    worker = Worker(Client(args.bridge, args.credentials), args.data)
    try:
        while True:
            worker.once()
            if not args.poll:
                break
            time.sleep(2)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
