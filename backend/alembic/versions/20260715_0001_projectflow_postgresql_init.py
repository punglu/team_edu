"""projectflow postgresql init

Revision ID: 20260715_0001
Revises:
Create Date: 2026-07-15 19:10:00
"""

from alembic import context, op
import sqlalchemy as sa


revision = "20260715_0001"
down_revision = None
branch_labels = None
depends_on = None


def _schema() -> str:
    schema = context.get_x_argument(as_dictionary=True).get("schema")
    if not schema:
        raise RuntimeError("Migration requires -x schema=<name> or DB_SCHEMA")
    return schema


def upgrade() -> None:
    schema = _schema()

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("owner_id", sa.String(length=100), nullable=False),
        sa.Column("owner_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("progress >= 0 AND progress <= 100", name="ck_projects_progress_range"),
        sa.CheckConstraint("due_date >= start_date", name="ck_projects_date_range"),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
        schema=schema,
    )
    op.create_index(
        "ix_projects_updated_at",
        "projects",
        ["updated_at"],
        unique=False,
        schema=schema,
    )

    op.create_table(
        "project_invited_members",
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], [f"{schema}.projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "position", name="pk_project_invited_members"),
        schema=schema,
    )

    op.create_table(
        "members",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id", name="pk_members"),
        schema=schema,
    )
    op.create_index("ix_members_active", "members", ["active"], unique=False, schema=schema)


def downgrade() -> None:
    schema = _schema()
    op.drop_index("ix_members_active", table_name="members", schema=schema)
    op.drop_table("members", schema=schema)
    op.drop_table("project_invited_members", schema=schema)
    op.drop_index("ix_projects_updated_at", table_name="projects", schema=schema)
    op.drop_table("projects", schema=schema)
