"""Immutable objects, project references and durable import journal."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade():
    op.create_table(
        "blobs",
        sa.Column("digest", sa.String(), primary_key=True),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("digest", sa.String(), sa.ForeignKey("blobs.digest"), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    op.create_index("ix_assets_project", "assets", ["project_id"])
    op.create_table(
        "operations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("digest", sa.String()),
        sa.Column("size", sa.Integer()),
        sa.Column("error", sa.String()),
        sa.Column("created_at", sa.String(), nullable=False),
    )


def downgrade():
    raise RuntimeError("Downgrade refused; restore a verified backup into a new location")
