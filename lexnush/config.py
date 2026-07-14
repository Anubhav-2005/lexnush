import os
from pathlib import Path


def environment_list(name):
    return tuple(value.strip() for value in os.getenv(name, "").split(",") if value.strip())


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("LEXNUSH_SECRET_KEY") or "dev-only-change-me"
    DATABASE_PATH = os.getenv("LEXNUSH_DATABASE_PATH")
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 128 * 1024
    MAX_FORM_MEMORY_SIZE = 64 * 1024
    MAX_FORM_PARTS = 20
    PREFERRED_URL_SCHEME = "http"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    SESSION_REFRESH_EACH_REQUEST = False
    TRUSTED_PROXY_COUNT = int(os.getenv("TRUSTED_PROXY_COUNT", "0"))
    TRUSTED_HOSTS = environment_list("LEXNUSH_TRUSTED_HOSTS") or None
    WTF_CSRF_FIELD_NAME = "_csrf_token"
    WTF_CSRF_TIME_LIMIT = 3600
    RATE_LIMIT_SEARCH = (60, 60)
    RATE_LIMIT_FORMS = (8, 15 * 60)
    CONTACT_MESSAGE_MAX_LENGTH = 3000
    CONTACT_MESSAGE_MIN_LENGTH = 20
    CONTACT_NAME_MAX_LENGTH = 120
    CONTACT_TOPIC_MAX_LENGTH = 120
    EMAIL_MAX_LENGTH = 254

    @staticmethod
    def init_app(app):
        if not app.config.get("DATABASE_PATH"):
            app.config["DATABASE_PATH"] = str(Path(app.instance_path) / "lexnush.sqlite3")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = True

    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        if app.config["SECRET_KEY"] == "dev-only-change-me":
            raise RuntimeError("Set SECRET_KEY before running LexNush in production.")
        if not app.config["TRUSTED_HOSTS"]:
            raise RuntimeError("Set LEXNUSH_TRUSTED_HOSTS before running LexNush in production.")


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    config_name = name or os.getenv("FLASK_ENV") or os.getenv("LEXNUSH_ENV") or "development"
    return CONFIGS.get(config_name, DevelopmentConfig)
