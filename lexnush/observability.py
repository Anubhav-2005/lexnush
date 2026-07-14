"""Logging and optional Sentry integration without personal-data logging."""

import logging
import re


class RedactingFilter(logging.Filter):
    _sensitive = re.compile(r"(password|authorization|api[_-]?key|secret|message|email)=?[^\s,]+", re.I)

    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = self._sensitive.sub(r"\1=[redacted]", record.msg)
        return True


def init_observability(app):
    for handler in app.logger.handlers:
        handler.addFilter(RedactingFilter())
    if app.config.get("SENTRY_DSN"):
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=app.config["SENTRY_DSN"], send_default_pii=False, traces_sample_rate=0.05)
        except ImportError:  # pragma: no cover - dependency is production required
            app.logger.warning("Sentry SDK is unavailable")
