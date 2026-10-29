import hashlib
import json
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from filelock import FileLock, Timeout

from voxfoundry.domain.errors import DomainError

MAX_AUDIO = 256 * 1024


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def private_root(root: Path) -> Path:
    root = root.expanduser().absolute()
    checkout = Path(__file__).resolve().parents[3]
    if root.resolve().is_relative_to(checkout):
        raise ValueError("Keep disposable POC data/credentials outside the checkout")
    if (root / "library.sqlite3").exists():
        raise ValueError("Use a separate disposable directory, not an existing VoxFoundry library")
    if root.is_symlink():
        raise ValueError("POC directory must not be a symlink")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    for child in root.iterdir():
        if child.is_symlink():
            raise ValueError("POC internal paths must not be symlinks")
    return root


class Queue:
    def __init__(self, root: Path, clock=time.time, lease_seconds=30):
        self.root = private_root(root)
        self.clock, self.lease_seconds = clock, lease_seconds
        self.lock = FileLock(str(self.root / ".bridge.lock"))
        try:
            self.lock.acquire(timeout=0)
        except Timeout as exc:
            raise ValueError("POC bridge data is already in use") from exc
        try:
            self.db = self.root / "queue.sqlite3"
            self.objects = self.root / "audio"
            self.objects.mkdir(exist_ok=True, mode=0o700)
            self.staging = self.root / "staging"
            self.staging.mkdir(exist_ok=True, mode=0o700)
            with self.connection() as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL,
                        text TEXT NOT NULL, text_digest TEXT NOT NULL,
                        state TEXT NOT NULL, progress INTEGER NOT NULL DEFAULT 0,
                        attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL DEFAULT 3,
                        lease_hash TEXT, lease_until REAL, audio_digest TEXT, audio_bytes INTEGER,
                        error TEXT, created_at REAL NOT NULL);
                    CREATE TABLE IF NOT EXISTS attempts (
                        job_id TEXT NOT NULL REFERENCES jobs(id), number INTEGER NOT NULL,
                        started_at REAL NOT NULL, lease_hash TEXT NOT NULL,
                        PRIMARY KEY(job_id, number));
                """)
                version = conn.execute("SELECT value FROM config WHERE key='version'").fetchone()
                if version and version[0] != "1":
                    raise ValueError("Unknown POC database version")
                conn.execute("INSERT OR IGNORE INTO config VALUES ('version','1')")
            credential = self.root / "worker-credential.json"
            if not credential.exists():
                with self.connection() as conn:
                    if conn.execute("SELECT value FROM config WHERE key='worker_hash'").fetchone():
                        raise ValueError(
                            "Worker credential missing; preserve the queue and re-pair explicitly"
                        )
                token = secrets.token_urlsafe(32)
                with open(
                    credential, "x", encoding="utf-8", opener=lambda p, f: os.open(p, f, 0o600)
                ) as stream:
                    json.dump({"token": token}, stream)
                with self.connection(write=True) as conn:
                    conn.execute("INSERT INTO config VALUES ('worker_hash',?)", (digest(token),))
            # Normal application credential loading; never log or return this value to a browser.
            token = json.loads(credential.read_text(encoding="utf-8"))["token"]
            with self.connection() as conn:
                expected = conn.execute(
                    "SELECT value FROM config WHERE key='worker_hash'"
                ).fetchone()
            if not expected or not secrets.compare_digest(expected[0], digest(token)):
                raise ValueError(
                    "Worker credential does not match bridge; preserve data and re-pair explicitly"
                )
            self.worker_hash = expected[0]
        except BaseException:
            self.close()
            raise

    @contextmanager
    def connection(self, write=False):
        conn = sqlite3.connect(self.db, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        try:
            conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def close(self):
        self.lock.release()

    def authorize(self, authorization):
        token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
        if not token or not secrets.compare_digest(digest(token), self.worker_hash):
            raise DomainError("Worker authentication failed", 401)
        with self.connection(write=True) as conn:
            conn.execute(
                "INSERT INTO config VALUES('worker_last_seen',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(self.clock()),),
            )

    def last_contact(self):
        with self.connection() as conn:
            row = conn.execute("SELECT value FROM config WHERE key='worker_last_seen'").fetchone()
        return {"seconds_since_contact": max(0, self.clock() - float(row[0])) if row else None}

    @staticmethod
    def public(row):
        return {
            key: row[key]
            for key in (
                "id",
                "request_id",
                "text",
                "text_digest",
                "state",
                "progress",
                "attempts",
                "error",
                "created_at",
                "audio_digest",
            )
        }

    def submit(self, request_id, text):
        with self.connection(write=True) as conn:
            old = conn.execute("SELECT * FROM jobs WHERE request_id=?", (request_id,)).fetchone()
            if old:
                if old["text_digest"] != digest(text):
                    raise DomainError("Request ID already belongs to different text", 409)
                return self.public(old)
            job_id = str(uuid4())
            conn.execute(
                "INSERT INTO jobs(id,request_id,text,text_digest,state,created_at) VALUES(?,?,?,?,?,?)",
                (job_id, request_id, text, digest(text), "queued", self.clock()),
            )
            return self.public(conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone())

    def list(self):
        with self.connection() as conn:
            return [
                self.public(r) for r in conn.execute("SELECT * FROM jobs ORDER BY created_at,id")
            ]

    def get(self, job_id):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                raise DomainError("Job not found", 404)
            return dict(row)

    def claim(self):
        with self.connection(write=True) as conn:
            conn.execute(
                "UPDATE jobs SET state='failed', error='Retry budget exhausted', lease_until=NULL WHERE state='leased' AND lease_until<=? AND attempts>=max_attempts",
                (self.clock(),),
            )
            row = conn.execute(
                "SELECT * FROM jobs WHERE state='queued' OR (state='leased' AND lease_until<=?) ORDER BY created_at,id LIMIT 1",
                (self.clock(),),
            ).fetchone()
            if not row:
                return None
            lease = secrets.token_urlsafe(32)
            attempt = row["attempts"] + 1
            expires = self.clock() + self.lease_seconds
            conn.execute(
                "UPDATE jobs SET state='leased',progress=0,attempts=?,lease_hash=?,lease_until=?,error=NULL WHERE id=?",
                (attempt, digest(lease), expires, row["id"]),
            )
            conn.execute(
                "INSERT INTO attempts VALUES(?,?,?,?)",
                (row["id"], attempt, self.clock(), digest(lease)),
            )
            return {
                **self.public(
                    conn.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone()
                ),
                "lease_token": lease,
                "lease_until": expires,
            }

    def leased(self, conn, job_id, lease, *, completed=False):
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise DomainError("Job not found", 404)
        same = secrets.compare_digest(row["lease_hash"] or "", digest(lease))
        if not same or (
            row["state"] != "leased" and not (completed and row["state"] == "succeeded")
        ):
            raise DomainError("Stale or invalid lease", 409)
        if row["state"] == "leased" and row["lease_until"] <= self.clock():
            raise DomainError("Lease expired; claim again", 409)
        return row

    def heartbeat(self, job_id, lease, progress):
        with self.connection(write=True) as conn:
            self.leased(conn, job_id, lease)
            conn.execute(
                "UPDATE jobs SET lease_until=?,progress=MAX(progress,?) WHERE id=?",
                (self.clock() + self.lease_seconds, progress, job_id),
            )
        return {"lease_until": self.clock() + self.lease_seconds}

    def complete(self, job_id, lease, audio_digest, size):
        with self.connection(write=True) as conn:
            row = self.leased(conn, job_id, lease, completed=True)
            if row["state"] == "succeeded":
                if row["audio_digest"] != audio_digest:
                    raise DomainError("Completion already has different bytes", 409)
                return self.public(row)
            conn.execute(
                "UPDATE jobs SET state='succeeded',progress=100,audio_digest=?,audio_bytes=?,error=NULL WHERE id=?",
                (audio_digest, size, job_id),
            )
            return self.public(conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone())

    def fail(self, job_id, lease):
        with self.connection(write=True) as conn:
            self.leased(conn, job_id, lease)
            conn.execute(
                "UPDATE jobs SET state='failed',error='Worker reported a test-generation failure',lease_until=NULL WHERE id=?",
                (job_id,),
            )

    def retry(self, job_id):
        with self.connection(write=True) as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                raise DomainError("Job not found", 404)
            if row["state"] != "failed":
                raise DomainError("Only failed jobs can be retried explicitly", 409)
            conn.execute(
                "UPDATE jobs SET state='queued',progress=0,max_attempts=attempts+3,lease_hash=NULL,error=NULL WHERE id=?",
                (job_id,),
            )
