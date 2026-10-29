from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table, Text

metadata = MetaData()
libraries = Table(
    "library",
    metadata,
    Column("id", String, primary_key=True),
    Column("created_at", String, nullable=False),
)
series = Table(
    "series",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("created_at", String, nullable=False),
)
projects = Table(
    "projects",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("series_id", String, ForeignKey("series.id")),
    Column("version", Integer, nullable=False),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
    Column("trashed_at", String),
)
blobs = Table(
    "blobs",
    metadata,
    Column("digest", String, primary_key=True),
    Column("size", Integer, nullable=False),
    Column("state", String, nullable=False),
)
assets = Table(
    "assets",
    metadata,
    Column("id", String, primary_key=True),
    Column("project_id", String, ForeignKey("projects.id"), nullable=False),
    Column("digest", String, ForeignKey("blobs.digest"), nullable=False),
    Column("filename", String, nullable=False),
    Column("created_at", String, nullable=False),
)
operations = Table(
    "operations",
    metadata,
    Column("id", String, primary_key=True),
    Column("project_id", String, ForeignKey("projects.id"), nullable=False),
    Column("asset_id", String, nullable=False),
    Column("filename", String, nullable=False),
    Column("state", String, nullable=False),
    Column("digest", String),
    Column("size", Integer),
    Column("error", String),
    Column("created_at", String, nullable=False),
)

# Phase 2 tables: migration constraints are also enforced in the database.
document_nodes = Table(
    "document_nodes",
    metadata,
    Column("id", String, primary_key=True),
    Column("project_id", String, ForeignKey("projects.id"), nullable=False),
    Column("parent_id", String),
    Column("title", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("position", Integer, nullable=False),
    Column("version", Integer, nullable=False),
    Column("active", Boolean, nullable=False),
    Column("original_asset_id", String),
    Column("head_revision_id", String),
    Column("references_json", Text, nullable=False),
)
document_drafts = Table(
    "document_drafts",
    metadata,
    Column("node_id", String, primary_key=True),
    Column("project_id", String, nullable=False),
    Column("text", Text, nullable=False),
    Column("version", Integer, nullable=False),
    Column("saved_at", String, nullable=False),
)
document_revisions = Table(
    "document_revisions",
    metadata,
    Column("id", String, primary_key=True),
    Column("node_id", String, nullable=False),
    Column("project_id", String, nullable=False),
    Column("parent_id", String),
    Column("restored_from", String),
    Column("digest", String, ForeignKey("blobs.digest"), nullable=False),
    Column("units_json", Text, nullable=False),
    Column("reason", String, nullable=False),
    Column("created_at", String, nullable=False),
)
project_snapshots = Table(
    "project_snapshots",
    metadata,
    Column("id", String, primary_key=True),
    Column("project_id", String, ForeignKey("projects.id"), nullable=False),
    Column("parent_id", String),
    Column("restored_from", String),
    Column("name", String, nullable=False),
    Column("manifest_json", Text, nullable=False),
    Column("created_at", String, nullable=False),
)
project_state = Table(
    "project_state",
    metadata,
    Column("project_id", String, ForeignKey("projects.id"), primary_key=True),
    Column("generation", Integer, nullable=False),
    Column("head_snapshot_id", String),
)
preset_versions = Table(
    "preset_versions",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("version", Integer, nullable=False),
    Column("settings_json", Text, nullable=False),
    Column("created_at", String, nullable=False),
)
project_settings = Table(
    "project_settings",
    metadata,
    Column("project_id", String, ForeignKey("projects.id"), primary_key=True),
    Column("version", Integer, nullable=False),
    Column("preset_id", String, ForeignKey("preset_versions.id")),
    Column("overrides_json", Text, nullable=False),
)

project_setting_versions = Table(
    "project_setting_versions",
    metadata,
    Column("project_id", String, ForeignKey("projects.id"), primary_key=True),
    Column("version", Integer, primary_key=True),
    Column("preset_id", String),
    Column("overrides_json", Text, nullable=False),
    Column("created_at", String, nullable=False),
)
