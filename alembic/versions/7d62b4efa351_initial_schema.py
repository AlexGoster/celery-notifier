"""Initial background task and notification schema."""

import sqlalchemy as sa

from alembic import op

revision = "7d62b4efa351"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "background_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("background_tasks.id"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("recipient", sa.String(200), nullable=False),
        sa.Column("subject", sa.String(200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("status", sa.String(20), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("background_tasks")
