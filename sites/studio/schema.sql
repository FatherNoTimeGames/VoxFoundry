-- First schema for a NEW, isolated Site D1 database. No runtime DDL.
-- Supported Sites binding/migration configuration must be verified before hosting.
-- Never apply this schema to the old manuscript or audio-proof databases.
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  archived_at INTEGER,
  last_op TEXT NOT NULL,
  UNIQUE(id, owner)
);
CREATE INDEX projects_owner ON projects(owner, archived_at, updated_at);
CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  owner TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  archived_at INTEGER,
  last_op TEXT NOT NULL,
  UNIQUE(id, owner),
  FOREIGN KEY(project_id, owner) REFERENCES projects(id, owner)
);
CREATE INDEX documents_project ON documents(owner, project_id, archived_at, updated_at);
CREATE TABLE document_revisions (
  id TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  document_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  archived_at INTEGER,
  created_at INTEGER NOT NULL,
  operation_id TEXT NOT NULL,
  UNIQUE(document_id, version),
  FOREIGN KEY(document_id, owner) REFERENCES documents(id, owner)
);
CREATE TABLE commands (
  owner TEXT NOT NULL,
  request_id TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  result_json TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  PRIMARY KEY(owner, request_id)
);
