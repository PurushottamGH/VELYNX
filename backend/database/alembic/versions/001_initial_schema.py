"""Initial schema — all VELYNX tables.

Revision ID: 001_initial
Revises: None
Create Date: 2026-05-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "episodes",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("prompt", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("confidence", sa.String(16), server_default="UNKNOWN"),
        sa.Column("source", sa.String(64)),
        sa.Column("tags", JSONB, server_default="[]"),
        sa.Column("kind", sa.String(32), server_default="learned"),
        sa.Column("importance", sa.Float, server_default="0.5"),
        sa.Column("embedding", JSONB),
        sa.Column("access_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "concepts",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("token", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("weight", sa.Float, server_default="0.0"),
        sa.Column("episodes", JSONB, server_default="[]"),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "reflections",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("answer", sa.Text),
        sa.Column("reasoning_quality", sa.Float),
        sa.Column("hallucination_risk", sa.Float),
        sa.Column("audit_issues", JSONB, server_default="[]"),
        sa.Column("improvements", JSONB, server_default="[]"),
        sa.Column("confidence_estimate", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "goals",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("priority", sa.Integer, server_default="5"),
        sa.Column("status", sa.String(16), server_default="active"),
        sa.Column("parent_id", sa.String(16), sa.ForeignKey("goals.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", JSONB, server_default="{}"),
    )

    op.create_table(
        "context_snapshots",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("session_id", sa.String(16), sa.ForeignKey("sessions.id"), nullable=True),
        sa.Column("snapshot", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "permanence",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("fact", sa.Text, nullable=False),
        sa.Column("score", sa.Float, server_default="0.5"),
        sa.Column("source", sa.String(64)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "source_trust",
        sa.Column("source_name", sa.String(64), primary_key=True),
        sa.Column("trust_score", sa.Float, server_default="1.0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("answer", sa.Text),
        sa.Column("rating", sa.Integer),
        sa.Column("correction", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "learned_rules",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("domains", JSONB, server_default="[]"),
        sa.Column("risk", sa.String(16), server_default="low"),
        sa.Column("status", sa.String(16), server_default="active"),
        sa.Column("cognitive_layer", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "learned_rules", "feedback", "source_trust", "permanence",
        "context_snapshots", "sessions", "goals", "reflections",
        "concepts", "episodes",
    ]:
        op.drop_table(table)
