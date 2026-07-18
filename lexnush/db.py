"""SQLAlchemy models and persistence helpers for LexNush."""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from flask import current_app
from flask_migrate import Config, Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, String, Text, inspect, select, text
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()
migrate = Migrate()


def utcnow():
    return datetime.now(timezone.utc)


def as_utc(value):
    """Normalise SQLite's naive timestamps and PostgreSQL timestamps for comparison."""
    return value.replace(tzinfo=timezone.utc) if value is not None and value.tzinfo is None else value


class ContactSubmission(db.Model):
    __tablename__ = "contact_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new", index=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(nullable=True)


class NewsletterSubscription(db.Model):
    __tablename__ = "newsletter_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="journal")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow, index=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    unsubscribed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class NewsletterToken(db.Model):
    __tablename__ = "newsletter_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(db.ForeignKey("newsletter_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    purpose: Mapped[str] = mapped_column(String(20), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow)

    __table_args__ = (Index("idx_newsletter_tokens_lookup", "subscription_id", "purpose", "expires_at"),)


class EmailOutboxEvent(db.Model):
    __tablename__ = "email_outbox_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recipient: Mapped[str] = mapped_column(String(254), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AdminAuditEvent(db.Model):
    __tablename__ = "admin_audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow, index=True)


def init_database(app):
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)


def verify_production_database():
    """Verify the deployed connection and required migrated schema without mutating it."""
    engine = db.engine
    if engine.dialect.name != "postgresql":
        raise RuntimeError(f"Expected PostgreSQL in production, connected to {engine.dialect.name!r} instead.")

    inspector = inspect(engine)
    required_tables = {
        "contact_submissions",
        "newsletter_subscriptions",
        "newsletter_tokens",
        "email_outbox_events",
        "admin_audit_events",
    }
    missing_tables = sorted(required_tables - set(inspector.get_table_names()))
    if missing_tables:
        raise RuntimeError("Production migration verification failed; missing tables: " + ", ".join(missing_tables))

    from alembic.config import Config

alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option(
    "script_location",
    str(Path(current_app.root_path).parent / "migrations"),
)

expected_revision = ScriptDirectory.from_config(alembic_cfg).get_current_head()
    with engine.connect() as connection:
        current_revision = MigrationContext.configure(connection).get_current_revision()
        database_name = connection.execute(text("SELECT current_database()")).scalar_one()
    if current_revision != expected_revision:
        raise RuntimeError(
            f"Production database {database_name!r} is at Alembic revision {current_revision!r}; "
            f"expected {expected_revision!r}."
        )
    return database_name, current_revision


def save_contact_submission(name, email, topic, message):
    contact = ContactSubmission(name=name, email=email, topic=topic, message=message)
    db.session.add(contact)
    db.session.flush()
    return contact


def get_or_create_subscription(email, source="journal"):
    subscription = db.session.scalar(select(NewsletterSubscription).where(NewsletterSubscription.email == email))
    if subscription is None:
        subscription = NewsletterSubscription(email=email, source=source)
        db.session.add(subscription)
        db.session.flush()
    elif subscription.status == "unsubscribed":
        subscription.status = "pending"
        subscription.unsubscribed_at = None
    return subscription


def create_newsletter_token(subscription, purpose):
    raw_token = secrets.token_urlsafe(32)
    token = NewsletterToken(
        subscription_id=subscription.id,
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        purpose=purpose,
        expires_at=utcnow() + timedelta(seconds=current_app.config["NEWSLETTER_TOKEN_MAX_AGE"]),
    )
    db.session.add(token)
    db.session.flush()
    return raw_token, token


def consume_newsletter_token(raw_token, purpose):
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    token = db.session.scalar(
        select(NewsletterToken).where(
            NewsletterToken.token_hash == token_hash,
            NewsletterToken.purpose == purpose,
        )
    )
    if not token or token.consumed_at or as_utc(token.expires_at) < utcnow():
        return None
    token.consumed_at = utcnow()
    return db.session.get(NewsletterSubscription, token.subscription_id)


def create_outbox_event(event_type, recipient, subject, payload_json):
    event = EmailOutboxEvent(
        event_type=event_type,
        recipient=recipient,
        subject=subject,
        payload_json=payload_json,
    )
    db.session.add(event)
    db.session.flush()
    return event


def audit_admin_action(admin_email, action, target_type=None, target_id=None, ip_hash=None):
    db.session.add(
        AdminAuditEvent(
            admin_email=admin_email,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            ip_hash=ip_hash,
        )
    )


def purge_personal_data(older_than_days):
    cutoff = utcnow() - timedelta(days=older_than_days)
    contacts = db.session.query(ContactSubmission).filter(ContactSubmission.created_at < cutoff).delete()
    subscribers = db.session.query(NewsletterSubscription).filter(NewsletterSubscription.created_at < cutoff).delete()
    db.session.query(EmailOutboxEvent).filter(EmailOutboxEvent.created_at < cutoff).delete()
    db.session.query(NewsletterToken).filter(NewsletterToken.expires_at < utcnow()).delete()
    db.session.commit()
    return contacts, subscribers


def backup_database(destination=None):
    """Create a consistent SQLite backup for local development only."""
    uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if not uri.startswith("sqlite:///"):
        raise RuntimeError("Use the managed PostgreSQL provider backup and restore process in production.")
    database_path = Path(uri.removeprefix("sqlite:///"))
    backup_dir = Path(destination) if destination else database_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{database_path.stem}-{utcnow().strftime('%Y%m%dT%H%M%SZ')}.sqlite3"
    source = sqlite3.connect(database_path)
    target = sqlite3.connect(backup_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return backup_path
