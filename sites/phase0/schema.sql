-- Isolated Phase 0 D1 database only. Apply through verified Sites migration tooling.
-- Never apply to the existing manuscript database. No request-time DDL.
CREATE TABLE devices (
  id TEXT PRIMARY KEY, owner TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
  revoked INTEGER NOT NULL DEFAULT 0 CHECK (revoked IN (0,1))
);
CREATE TABLE jobs (
  id TEXT PRIMARY KEY, owner TEXT NOT NULL, request_id TEXT NOT NULL,
  text TEXT NOT NULL, text_digest TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'queued' CHECK(state IN ('queued','running','succeeded')),
  progress INTEGER NOT NULL DEFAULT 0, attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3, device_id TEXT,
  lease_hash TEXT, lease_until INTEGER, audio_digest TEXT, object_key TEXT,
  created_at INTEGER NOT NULL, UNIQUE(owner, request_id)
);
CREATE INDEX jobs_claim ON jobs(owner, state, created_at);
CREATE TABLE attempts (
  job_id TEXT NOT NULL REFERENCES jobs(id), number INTEGER NOT NULL,
  device_id TEXT NOT NULL, lease_hash TEXT NOT NULL, started_at INTEGER NOT NULL,
  PRIMARY KEY(job_id, number)
);
