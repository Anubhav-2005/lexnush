from pathlib import Path

import click
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .admin import admin_bp
from .auth import init_login
from .config import get_config
from .db import backup_database, db, init_database, purge_personal_data, verify_production_database
from .mailer import retry_pending_outbox
from .observability import init_observability
from .rate_limit import init_rate_limiting
from .routes import api_bp, main_bp
from .security import init_security


def create_app(config_name=None, config_overrides=None):
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        instance_path=str(project_root / "instance"),
        instance_relative_config=True,
        static_folder=str(project_root / "static"),
        template_folder=str(project_root / "templates"),
    )
    config = get_config(config_name)
    app.config.from_object(config)
    if config_overrides:
        app.config.update(config_overrides)
    config.init_app(app)

    # Only trust forwarded request data when the deployment explicitly declares
    # how many reverse proxies sit in front of the app. This keeps host and IP
    # based controls from accepting client-supplied forwarding headers by default.
    trusted_proxy_count = app.config.get("TRUSTED_PROXY_COUNT", 0)
    if trusted_proxy_count:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=trusted_proxy_count,
            x_proto=trusted_proxy_count,
            x_host=trusted_proxy_count,
        )

    init_database(app)
    init_rate_limiting(app)
    init_login(app)
    init_security(app)
    init_observability(app)
    app.context_processor(
        lambda: {
            "public_base_url": app.config["PUBLIC_BASE_URL"],
            "turnstile_site_key": app.config.get("TURNSTILE_SITE_KEY", ""),
        }
    )
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Initialized LexNush development database.")

    @app.cli.command("backup-db")
    def backup_db_command():
        backup_path = backup_database()
        print(f"Backed up LexNush database to {backup_path}")

    @app.cli.command("purge-personal-data")
    @click.option("--older-than-days", type=click.IntRange(min=1), required=True)
    def purge_personal_data_command(older_than_days):
        contacts, newsletter_signups = purge_personal_data(older_than_days)
        print(f"Purged {contacts} contact submissions and {newsletter_signups} newsletter signups.")

    @app.cli.command("retry-email-outbox")
    @click.option("--limit", type=click.IntRange(min=1, max=1000), default=100)
    def retry_email_outbox_command(limit):
        print(f"Attempted delivery for {retry_pending_outbox(limit)} queued email events.")

    @app.cli.command("verify-production-database")
    def verify_production_database_command():
        """Fail deployment unless the connected PostgreSQL schema is at Alembic head."""
        database_name, revision = verify_production_database()
        print(f"Verified PostgreSQL database {database_name!r} at Alembic revision {revision}.")

    return app
