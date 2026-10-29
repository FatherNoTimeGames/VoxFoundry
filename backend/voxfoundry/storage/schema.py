from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, Text

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
