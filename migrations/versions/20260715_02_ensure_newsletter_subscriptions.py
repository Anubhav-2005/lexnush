"""ensure newsletter subscription schema exists on previously stamped databases

Revision ID: 20260715_02
Revises: 20260715_01
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_02"
down_revision = "20260715_01"
branch_labels = None
depends_on = None


def upgrade():
    """Repair only a missing table; never replace or delete existing subscriptions."""
    inspector = sa.inspect(op.get_bind())
    if "newsletter_subscriptions" not in inspector.get_table_names():
        op.create_table(
            "newsletter_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=254), nullable=False, unique=True),
            sa.Column("source", sa.String(length=80), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        )

    index_names = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("newsletter_subscriptions")}
    if "ix_newsletter_subscriptions_status" not in index_names:
        op.create_index("ix_newsletter_subscriptions_status", "newsletter_subscriptions", ["status"])
    if "ix_newsletter_subscriptions_created_at" not in index_names:
        op.create_index("ix_newsletter_subscriptions_created_at", "newsletter_subscriptions", ["created_at"])


def downgrade():
    # The preceding migration owns this durable table and may contain real data.
    # A downgrade must not delete subscriber records merely because this repair
    # revision was applied.
    pass
