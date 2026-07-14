from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from flask import current_app, g


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db():
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path, timeout=5)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA busy_timeout = 5000")
        g.db.execute("PRAGMA journal_mode = WAL")
        g.db.execute("PRAGMA secure_delete = ON")
        g.db.execute("PRAGMA trusted_schema = OFF")
        ensure_schema(g.db)
    return g.db


def ensure_schema(db):
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS contact_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            topic TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_contact_submissions_created_at
        ON contact_submissions(created_at);

        CREATE TABLE IF NOT EXISTS newsletter_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_newsletter_signups_created_at
        ON newsletter_signups(created_at);

        CREATE TABLE IF NOT EXISTS rate_limit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT NOT NULL,
            client_key TEXT NOT NULL,
            created_at REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_rate_limit_events_scope_client_created
        ON rate_limit_events(scope, client_key, created_at);
        """
    )
    db.commit()


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def save_contact_submission(name, email, topic, message):
    db = get_db()
    db.execute(
        """
        INSERT INTO contact_submissions (name, email, topic, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, email, topic, message, now_iso()),
    )
    db.commit()


def save_newsletter_signup(email, source="journal"):
    db = get_db()
    db.execute(
        """
        INSERT OR IGNORE INTO newsletter_signups (email, source, created_at)
        VALUES (?, ?, ?)
        """,
        (email, source, now_iso()),
    )
    db.commit()


def backup_database(destination=None):
    database_path = Path(current_app.config["DATABASE_PATH"])
    if not database_path.exists():
        ensure_schema(get_db())

    backup_dir = Path(destination) if destination else database_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{database_path.stem}-{now_iso().replace(':', '-')}.sqlite3"
    # SQLite's backup API includes committed WAL pages. A filesystem copy can
    # silently omit recent writes while WAL mode is enabled.
    source = sqlite3.connect(database_path)
    destination_connection = sqlite3.connect(backup_path)
    try:
        source.backup(destination_connection)
    finally:
        destination_connection.close()
        source.close()
    return backup_path


def purge_personal_data(older_than_days):
    """Purge aged contact and newsletter data for a retention-policy job."""
    cutoff = datetime.now(timezone.utc).timestamp() - older_than_days * 24 * 60 * 60
    cutoff_iso = datetime.fromtimestamp(cutoff, timezone.utc).isoformat(timespec="seconds")
    db = get_db()
    contact_result = db.execute("DELETE FROM contact_submissions WHERE created_at < ?", (cutoff_iso,))
    newsletter_result = db.execute("DELETE FROM newsletter_signups WHERE created_at < ?", (cutoff_iso,))
    db.commit()
    return contact_result.rowcount, newsletter_result.rowcount
