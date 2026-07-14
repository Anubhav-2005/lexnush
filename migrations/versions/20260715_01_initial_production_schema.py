"""initial production schema

Revision ID: 20260715_01
Revises:
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    def ensure_index(table_name, index_name, columns):
        index_names = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}
        if index_name not in index_names:
            op.create_index(index_name, table_name, columns)

    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "contact_submissions" not in tables:
        op.create_table(
            "contact_submissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("email", sa.String(length=254), nullable=False),
            sa.Column("topic", sa.String(length=120), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        )
    else:
        columns = {column["name"] for column in inspector.get_columns("contact_submissions")}
        if "status" not in columns:
            op.add_column("contact_submissions", sa.Column("status", sa.String(length=20), nullable=False, server_default="new"))
        if "reviewed_at" not in columns:
            op.add_column("contact_submissions", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
        if "replied_at" not in columns:
            op.add_column("contact_submissions", sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True))
    ensure_index("contact_submissions", "ix_contact_submissions_email", ["email"])
    ensure_index("contact_submissions", "ix_contact_submissions_status", ["status"])
    ensure_index("contact_submissions", "ix_contact_submissions_created_at", ["created_at"])
    if "newsletter_subscriptions" not in tables:
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
    ensure_index("newsletter_subscriptions", "ix_newsletter_subscriptions_status", ["status"])
    ensure_index("newsletter_subscriptions", "ix_newsletter_subscriptions_created_at", ["created_at"])
    if "newsletter_signups" in tables:
        insert_prefix = "INSERT OR IGNORE" if op.get_bind().dialect.name == "sqlite" else "INSERT"
        conflict_clause = "" if op.get_bind().dialect.name == "sqlite" else " ON CONFLICT (email) DO NOTHING"
        op.execute(
            f"{insert_prefix} INTO newsletter_subscriptions (email, source, status, created_at) "
            "SELECT email, source, 'pending', created_at FROM newsletter_signups"
            f"{conflict_clause}"
        )
    if "newsletter_tokens" not in tables:
        op.create_table(
            "newsletter_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("subscription_id", sa.Integer(), sa.ForeignKey("newsletter_subscriptions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
            sa.Column("purpose", sa.String(length=20), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
    ensure_index("newsletter_tokens", "ix_newsletter_tokens_subscription_id", ["subscription_id"])
    ensure_index("newsletter_tokens", "ix_newsletter_tokens_expires_at", ["expires_at"])
    ensure_index("newsletter_tokens", "idx_newsletter_tokens_lookup", ["subscription_id", "purpose", "expires_at"])
    if "email_outbox_events" not in tables:
        op.create_table(
            "email_outbox_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("event_type", sa.String(length=50), nullable=False),
            sa.Column("recipient", sa.String(length=254), nullable=False),
            sa.Column("subject", sa.String(length=255), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False),
            sa.Column("provider_message_id", sa.String(length=255), nullable=True),
            sa.Column("last_error", sa.String(length=200), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        )
    ensure_index("email_outbox_events", "ix_email_outbox_events_event_type", ["event_type"])
    ensure_index("email_outbox_events", "ix_email_outbox_events_status", ["status"])
    ensure_index("email_outbox_events", "ix_email_outbox_events_created_at", ["created_at"])
    if "admin_audit_events" not in tables:
        op.create_table(
            "admin_audit_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("admin_email", sa.String(length=254), nullable=False),
            sa.Column("action", sa.String(length=80), nullable=False),
            sa.Column("target_type", sa.String(length=80), nullable=True),
            sa.Column("target_id", sa.String(length=80), nullable=True),
            sa.Column("ip_hash", sa.String(length=64), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
    ensure_index("admin_audit_events", "ix_admin_audit_events_admin_email", ["admin_email"])
    ensure_index("admin_audit_events", "ix_admin_audit_events_action", ["action"])
    ensure_index("admin_audit_events", "ix_admin_audit_events_created_at", ["created_at"])


def downgrade():
    op.drop_table("admin_audit_events")
    op.drop_table("email_outbox_events")
    op.drop_table("newsletter_tokens")
    op.drop_table("newsletter_subscriptions")
    op.drop_table("contact_submissions")
