import hashlib
import time

from flask import current_app, has_app_context, request

from .db import get_db



def client_identifier():
    # ProxyFix normalizes this value when trusted proxies are configured. Reading
    # X-Forwarded-For directly would let any client select its own rate-limit key.
    remote_addr = request.remote_addr or "unknown"
    return remote_addr


def client_key():
    return hashlib.sha256(client_identifier().encode("utf-8")).hexdigest()


def is_rate_limited(scope, limit, window_seconds):
    """Apply an atomic, database-backed limit that works across Gunicorn workers."""
    now = time.time()
    cutoff = now - window_seconds
    key = client_key()
    db = get_db()

    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM rate_limit_events WHERE created_at < ?", (cutoff,))
        count = db.execute(
            "SELECT COUNT(*) FROM rate_limit_events WHERE scope = ? AND client_key = ? AND created_at >= ?",
            (scope, key, cutoff),
        ).fetchone()[0]
        if count >= limit:
            db.commit()
            return True
        db.execute(
            "INSERT INTO rate_limit_events (scope, client_key, created_at) VALUES (?, ?, ?)",
            (scope, key, now),
        )
        db.commit()
        return False
    except Exception:
        db.rollback()
        current_app.logger.exception("Rate-limit storage failed")
        # Limits protect public endpoints; fail closed when their storage is unavailable.
        return True


def clear_rate_limits():
    if has_app_context():
        db = get_db()
        db.execute("DELETE FROM rate_limit_events")
        db.commit()
