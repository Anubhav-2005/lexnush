"""Environment-backed configuration with production fail-fast checks."""

import os
from pathlib import Path

from sqlalchemy.engine import make_url


def environment_list(name):
    return tuple(value.strip() for value in os.getenv(name, "").split(",") if value.strip())


def environment_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def normalize_database_url(database_url):
    """Use the installed Psycopg 3 driver for Render/PostgreSQL URLs."""
    database_url = (database_url or "").strip()
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql+psycopg2://"):
        return database_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    return database_url


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("LEXNUSH_SECRET_KEY") or "dev-only-change-me"
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    REDIS_URL = os.getenv("REDIS_URL", "memory://")
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    MAX_CONTENT_LENGTH = 128 * 1024
    MAX_FORM_MEMORY_SIZE = 64 * 1024
    MAX_FORM_PARTS = 20
    STATIC_SEND_FILE_MAX_AGE_DEFAULT = 31_536_000
    PREFERRED_URL_SCHEME = "http"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    SESSION_REFRESH_EACH_REQUEST = False
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8
    TRUSTED_PROXY_COUNT = int(os.getenv("TRUSTED_PROXY_COUNT", "0"))
    TRUSTED_HOSTS = environment_list("LEXNUSH_TRUSTED_HOSTS") or None
    WTF_CSRF_FIELD_NAME = "_csrf_token"
    WTF_CSRF_TIME_LIMIT = 3600
    RATE_LIMIT_STORAGE_URI = REDIS_URL
    RATE_LIMIT_SEARCH = "60 per minute"
    RATE_LIMIT_CONTACT = "5 per 15 minutes"
    RATE_LIMIT_NEWSLETTER = "5 per 15 minutes"
    RATE_LIMIT_LOGIN = "5 per 15 minutes"
    RATE_LIMIT_CONFIRM = "10 per hour"
    CONTACT_MESSAGE_MAX_LENGTH = 3000
    CONTACT_MESSAGE_MIN_LENGTH = 20
    CONTACT_NAME_MAX_LENGTH = 120
    CONTACT_TOPIC_MAX_LENGTH = 120
    EMAIL_MAX_LENGTH = 254
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "365"))
    NEWSLETTER_TOKEN_MAX_AGE = int(os.getenv("NEWSLETTER_TOKEN_MAX_AGE", str(60 * 60 * 24 * 3)))
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "")
    CONTACT_RECIPIENT_EMAIL = os.getenv("CONTACT_RECIPIENT_EMAIL", "")
    EMAIL_DELIVERY_ENABLED = environment_bool("EMAIL_DELIVERY_ENABLED", False)
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
    TURNSTILE_REQUIRED = environment_bool("TURNSTILE_REQUIRED", False)
    TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")

    @staticmethod
    def init_app(app):
        database_url = normalize_database_url(app.config.get("DATABASE_URL"))
        if database_url:
            # Render supplies postgresql://; this application uses Psycopg 3.
            app.config["DATABASE_URL"] = database_url
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        elif not app.config.get("SQLALCHEMY_DATABASE_URI"):
            database_path = Path(app.instance_path) / "lexnush.sqlite3"
            database_path.parent.mkdir(parents=True, exist_ok=True)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
        app.config["RATELIMIT_STORAGE_URI"] = app.config.get("REDIS_URL", "memory://")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    EMAIL_DELIVERY_ENABLED = False
    ADMIN_EMAIL = "admin@example.test"
    # This deterministic test-only Argon2 hash is never accepted in production.
    ADMIN_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$jozGG73RU5wxD5lbm6h6Sg$7Tm6CcWDnVgXhcG+Ck08g9sfk7fYCv0KJrABWGg+tBg"


class ProductionConfig(BaseConfig):
    DEBUG = False
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = True
    EMAIL_DELIVERY_ENABLED = True

    @staticmethod
    def init_app(app):
        # Validate before BaseConfig can ever choose the development SQLite
        # fallback. A web process connected to an ephemeral SQLite file can
        # appear healthy but has neither the production schema nor durable data.
        database_url = normalize_database_url(app.config.get("DATABASE_URL"))
        app.config["DATABASE_URL"] = database_url

        BaseConfig.init_app(app)
        missing = []
        required = {
            "SECRET_KEY": app.config.get("SECRET_KEY") != "dev-only-change-me",
            "DATABASE_URL": bool(app.config.get("DATABASE_URL")),
            "REDIS_URL": bool(app.config.get("REDIS_URL")) and app.config.get("REDIS_URL") != "memory://",
            "PUBLIC_BASE_URL": str(app.config.get("PUBLIC_BASE_URL", "")).startswith("https://"),
            "LEXNUSH_TRUSTED_HOSTS": bool(app.config.get("TRUSTED_HOSTS")),
            "RESEND_API_KEY": bool(app.config.get("RESEND_API_KEY")),
            "MAIL_FROM": bool(app.config.get("MAIL_FROM")),
            "CONTACT_RECIPIENT_EMAIL": bool(app.config.get("CONTACT_RECIPIENT_EMAIL")),
            "ADMIN_EMAIL": bool(app.config.get("ADMIN_EMAIL")),
            "ADMIN_PASSWORD_HASH": str(app.config.get("ADMIN_PASSWORD_HASH", "")).startswith("$argon2"),
        }
        for name, ready in required.items():
            if not ready:
                missing.append(name)
        if missing:
            raise RuntimeError("Missing or unsafe production configuration: " + ", ".join(missing))

        try:
            database = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
        except Exception as exc:
            raise RuntimeError("DATABASE_URL is not a valid SQLAlchemy PostgreSQL URL.") from exc
        if database.get_backend_name() != "postgresql" or not database.host:
            raise RuntimeError(
                "Production DATABASE_URL must be a Render PostgreSQL connection string; "
                "SQLite and hostless database URLs are not permitted."
            )


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    # LEXNUSH_ENV is the explicit application setting. Render detection is a
    # safety net: a missed environment variable must fail closed, never fall
    # back to a local SQLite database in a deployed web service.
    config_name = (name or os.getenv("LEXNUSH_ENV") or os.getenv("FLASK_ENV") or "").strip().lower()
    is_render = os.getenv("RENDER", "").lower() == "true"
    if config_name and config_name not in CONFIGS:
        if is_render:
            raise RuntimeError(f"Unsupported production environment name: {config_name!r}.")
        return DevelopmentConfig
    if not config_name and os.getenv("RENDER", "").lower() == "true":
        config_name = "production"
    config_name = config_name or "development"
    return CONFIGS.get(config_name, DevelopmentConfig)
