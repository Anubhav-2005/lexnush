"""Single-operator authentication sourced from secure environment variables."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from flask import current_app
from flask_login import LoginManager, UserMixin

login_manager = LoginManager()
login_manager.login_view = "admin.login"
login_manager.login_message = "Please sign in to continue."


class ConfigAdmin(UserMixin):
    def __init__(self, email):
        self.email = email
        self.id = email


@login_manager.user_loader
def load_user(user_id):
    configured = current_app.config.get("ADMIN_EMAIL", "")
    if configured and user_id == configured:
        return ConfigAdmin(configured)
    return None


def verify_admin_password(password):
    try:
        return PasswordHasher().verify(current_app.config["ADMIN_PASSWORD_HASH"], password)
    except (InvalidHashError, VerifyMismatchError):
        return False


def init_login(app):
    login_manager.init_app(app)
