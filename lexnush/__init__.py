from pathlib import Path

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import get_config
from .db import backup_database, close_db, ensure_schema, get_db
from .routes import api_bp, main_bp
from .security import init_security


def create_app(config_name=None):
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

    init_security(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.cli.command("init-db")
    def init_db_command():
        ensure_schema(get_db())
        print("Initialized LexNush database.")

    @app.cli.command("backup-db")
    def backup_db_command():
        backup_path = backup_database()
        print(f"Backed up LexNush database to {backup_path}")

    return app
