"""Public form honeypot and optional Cloudflare Turnstile verification."""

import requests
from flask import current_app, request


def honeypot_tripped(form):
    return bool((form.get("website") or "").strip())


def verify_turnstile(token):
    if not current_app.config.get("TURNSTILE_REQUIRED"):
        return True
    if not token or not current_app.config.get("TURNSTILE_SECRET_KEY"):
        return False
    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": current_app.config["TURNSTILE_SECRET_KEY"],
                "response": token,
                "remoteip": request.remote_addr,
            },
            timeout=5,
        )
        return bool(response.ok and response.json().get("success"))
    except requests.RequestException:
        current_app.logger.warning("Turnstile verification service unavailable")
        return False
