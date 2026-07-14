import re

from flask import current_app

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_text(value, max_length):
    cleaned = " ".join((value or "").strip().split())
    return cleaned[:max_length]


def validate_email(value):
    email = normalize_text(value, current_app.config["EMAIL_MAX_LENGTH"]).lower()
    if not EMAIL_RE.match(email):
        return email, "Please enter a valid email address."
    return email, None


def validate_contact_form(form):
    name = normalize_text(form.get("name"), current_app.config["CONTACT_NAME_MAX_LENGTH"])
    email, email_error = validate_email(form.get("email"))
    topic = normalize_text(form.get("topic"), current_app.config["CONTACT_TOPIC_MAX_LENGTH"])
    message = normalize_text(form.get("message"), current_app.config["CONTACT_MESSAGE_MAX_LENGTH"])
    data = {"name": name, "email": email, "topic": topic, "message": message}
    errors = {}

    if len(name) < 2:
        errors["name"] = "Please enter your name."
    if email_error:
        errors["email"] = email_error
    if len(topic) < 3:
        errors["topic"] = "Please include a short topic."
    if len(message) < current_app.config["CONTACT_MESSAGE_MIN_LENGTH"]:
        errors["message"] = "Please share a little more detail."

    return data, errors
