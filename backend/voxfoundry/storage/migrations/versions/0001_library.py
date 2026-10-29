"""Initial central library. Migrations are frozen, independent of runtime models."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "library",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    op.create_table(
        "series",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("series_id", sa.String(), sa.ForeignKey("series.id")),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.Column("trashed_at", sa.String()),
    )


def downgrade():
    raise RuntimeError("Downgrade refused; restore a verified backup into a new location")
