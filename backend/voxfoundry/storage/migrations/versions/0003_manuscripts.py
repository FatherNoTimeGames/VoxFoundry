"""Project-scoped manuscript history, snapshots and pronunciation settings."""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade():
    op.create_index("uq_assets_id_project", "assets", ["id", "project_id"], unique=True)
    op.create_table(
        "document_nodes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("parent_id", sa.String()),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("original_asset_id", sa.String()),
        sa.Column("head_revision_id", sa.String()),
        sa.Column("references_json", sa.Text(), nullable=False),
        sa.UniqueConstraint("id", "project_id"),
        sa.ForeignKeyConstraint(
            ["parent_id", "project_id"], ["document_nodes.id", "document_nodes.project_id"]
        ),
        sa.ForeignKeyConstraint(
            ["original_asset_id", "project_id"], ["assets.id", "assets.project_id"]
        ),
        sa.ForeignKeyConstraint(
            ["head_revision_id", "id", "project_id"],
            [
                "document_revisions.id",
                "document_revisions.node_id",
                "document_revisions.project_id",
            ],
        ),
    )
    op.create_table(
        "document_drafts",
        sa.Column("node_id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("saved_at", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["node_id", "project_id"], ["document_nodes.id", "document_nodes.project_id"]
        ),
    )
    op.create_table(
        "document_revisions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String()),
        sa.Column("restored_from", sa.String()),
        sa.Column("digest", sa.String(), sa.ForeignKey("blobs.digest"), nullable=False),
        sa.Column("units_json", sa.Text(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.UniqueConstraint("id", "node_id", "project_id"),
        sa.ForeignKeyConstraint(
            ["node_id", "project_id"], ["document_nodes.id", "document_nodes.project_id"]
        ),
        sa.ForeignKeyConstraint(
            ["parent_id", "node_id", "project_id"],
            [
                "document_revisions.id",
                "document_revisions.node_id",
                "document_revisions.project_id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["restored_from", "node_id", "project_id"],
            [
                "document_revisions.id",
                "document_revisions.node_id",
                "document_revisions.project_id",
            ],
        ),
    )
    op.create_table(
        "project_snapshots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("parent_id", sa.String()),
        sa.Column("restored_from", sa.String()),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("manifest_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.UniqueConstraint("id", "project_id"),
        sa.ForeignKeyConstraint(
            ["parent_id", "project_id"], ["project_snapshots.id", "project_snapshots.project_id"]
        ),
        sa.ForeignKeyConstraint(
            ["restored_from", "project_id"],
            ["project_snapshots.id", "project_snapshots.project_id"],
        ),
    )
    op.create_table(
        "project_state",
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("head_snapshot_id", sa.String()),
        sa.ForeignKeyConstraint(
            ["head_snapshot_id", "project_id"],
            ["project_snapshots.id", "project_snapshots.project_id"],
        ),
    )
    op.create_table(
        "preset_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("settings_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.UniqueConstraint("name", "version"),
    )
    op.create_table(
        "project_settings",
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("preset_id", sa.String(), sa.ForeignKey("preset_versions.id")),
        sa.Column("overrides_json", sa.Text(), nullable=False),
    )
    op.create_table(
        "project_setting_versions",
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("version", sa.Integer(), primary_key=True),
        sa.Column("preset_id", sa.String(), sa.ForeignKey("preset_versions.id")),
        sa.Column("overrides_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    for table in (
        "document_revisions",
        "project_snapshots",
        "preset_versions",
        "project_setting_versions",
    ):
        for action in ("UPDATE", "DELETE"):
            op.execute(
                f"CREATE TRIGGER immutable_{table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT, 'Immutable history'); END"
            )


def downgrade():
    raise RuntimeError("Downgrade refused; restore a verified backup into a new location")
