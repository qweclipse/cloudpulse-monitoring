"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


monitor_status = sa.Enum("UNKNOWN", "UP", "DOWN", name="monitor_status")
check_status = sa.Enum("SUCCESS", "FAILED", name="check_status")
incident_status = sa.Enum("OPEN", "RESOLVED", name="incident_status")


def upgrade() -> None:
    op.create_table(
        "monitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "interval_seconds",
            sa.Integer(),
            server_default=sa.text("60"),
            nullable=False,
        ),
        sa.Column(
            "expected_status_code",
            sa.Integer(),
            server_default=sa.text("200"),
            nullable=False,
        ),
        sa.Column(
            "timeout_seconds",
            sa.Integer(),
            server_default=sa.text("10"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "current_status",
            monitor_status,
            server_default=sa.text("'UNKNOWN'"),
            nullable=False,
        ),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_monitors_id"), "monitors", ["id"], unique=False)

    op.create_table(
        "check_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("monitor_id", sa.Integer(), nullable=False),
        sa.Column("status", check_status, nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["monitor_id"], ["monitors.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_check_results_id"), "check_results", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_check_results_monitor_id"),
        "check_results",
        ["monitor_id"],
        unique=False,
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("monitor_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            incident_status,
            server_default=sa.text("'OPEN'"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["monitor_id"], ["monitors.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_incidents_id"), "incidents", ["id"], unique=False)
    op.create_index(
        op.f("ix_incidents_monitor_id"), "incidents", ["monitor_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_incidents_monitor_id"), table_name="incidents")
    op.drop_index(op.f("ix_incidents_id"), table_name="incidents")
    op.drop_table("incidents")

    op.drop_index(op.f("ix_check_results_monitor_id"), table_name="check_results")
    op.drop_index(op.f("ix_check_results_id"), table_name="check_results")
    op.drop_table("check_results")

    op.drop_index(op.f("ix_monitors_id"), table_name="monitors")
    op.drop_table("monitors")

    bind = op.get_bind()
    incident_status.drop(bind, checkfirst=True)
    check_status.drop(bind, checkfirst=True)
    monitor_status.drop(bind, checkfirst=True)
