"""Add token_prefix column and index to agents table for O(1) token lookup.

Revision ID: d4e5f6a7b8c9
Revises: a9b1c2d3e4f7
Create Date: 2026-04-01 00:00:00.000000

NOTE: Existing agents will have token_prefix = NULL after this migration.
Agents with NULL token_prefix will NOT be able to authenticate until they
rotate their token (which will populate token_prefix) or until an operator
performs a manual backfill using the raw token values.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "a9b1c2d3e4f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add token_prefix VARCHAR(8) column and ix_agents_token_prefix index to agents."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("agents")}

    if "token_prefix" not in columns:
        op.add_column(
            "agents",
            sa.Column("token_prefix", sa.String(8), nullable=True),
        )

    indexes = {idx["name"] for idx in inspector.get_indexes("agents")}
    if "ix_agents_token_prefix" not in indexes:
        op.create_index(
            "ix_agents_token_prefix",
            "agents",
            ["token_prefix"],
        )


def downgrade() -> None:
    """Remove ix_agents_token_prefix index and token_prefix column from agents."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    indexes = {idx["name"] for idx in inspector.get_indexes("agents")}
    if "ix_agents_token_prefix" in indexes:
        op.drop_index("ix_agents_token_prefix", table_name="agents")

    columns = {c["name"] for c in inspector.get_columns("agents")}
    if "token_prefix" in columns:
        op.drop_column("agents", "token_prefix")
