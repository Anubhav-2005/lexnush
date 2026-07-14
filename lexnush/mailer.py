"""Transactional email outbox using Resend's HTTPS API."""

from __future__ import annotations

import html
import json

import requests
from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .db import EmailOutboxEvent, create_outbox_event, db, utcnow


def newsletter_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="lexnush-newsletter-token-v1")


def signed_newsletter_token(subscription_id, raw_token, purpose):
    return newsletter_serializer().dumps(
        {"subscription_id": subscription_id, "token": raw_token, "purpose": purpose}
    )


def read_signed_newsletter_token(value, purpose):
    try:
        data = newsletter_serializer().loads(
            value, max_age=current_app.config["NEWSLETTER_TOKEN_MAX_AGE"]
        )
    except (BadSignature, SignatureExpired):
        return None
    if data.get("purpose") != purpose:
        return None
    return data


def absolute_url(path):
    return f"{current_app.config['PUBLIC_BASE_URL'].rstrip('/')}{path}"


def queue_contact_notification(contact):
    payload = {
        "html": (
            "<h1>New LexNush inquiry</h1>"
            f"<p><strong>Name:</strong> {html.escape(contact.name)}</p>"
            f"<p><strong>Email:</strong> {html.escape(contact.email)}</p>"
            f"<p><strong>Topic:</strong> {html.escape(contact.topic)}</p>"
            f"<p><strong>Message:</strong><br>{html.escape(contact.message).replace(chr(10), '<br>')}</p>"
        )
    }
    return create_outbox_event(
        "contact-owner-notification",
        current_app.config["CONTACT_RECIPIENT_EMAIL"],
        f"New LexNush inquiry: {contact.topic}",
        json.dumps(payload),
    )


def queue_newsletter_confirmation(subscription, signed_token):
    confirm_url = absolute_url(f"/newsletter/confirm/{signed_token}")
    payload = {
        "html": (
            "<h1>Confirm your LexNush subscription</h1>"
            "<p>Confirm your email to receive occasional legal briefings.</p>"
            f'<p><a href="{html.escape(confirm_url, quote=True)}">Confirm subscription</a></p>'
            "<p>If you did not request this, you can ignore this email.</p>"
        )
    }
    return create_outbox_event(
        "newsletter-confirmation",
        subscription.email,
        "Confirm your LexNush subscription",
        json.dumps(payload),
    )


def queue_unsubscribe_confirmation(subscription):
    payload = {"html": "<p>You have been unsubscribed from LexNush updates.</p>"}
    return create_outbox_event(
        "newsletter-unsubscribe-confirmation",
        subscription.email,
        "You have been unsubscribed from LexNush",
        json.dumps(payload),
    )


def deliver_outbox_event(event):
    """Attempt one delivery. Payload contents are intentionally never logged."""
    if not current_app.config.get("EMAIL_DELIVERY_ENABLED"):
        return event
    event.attempts += 1
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {current_app.config['RESEND_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "from": current_app.config["MAIL_FROM"],
                "to": [event.recipient],
                "subject": event.subject,
                **json.loads(event.payload_json),
            },
            timeout=10,
        )
        response.raise_for_status()
        event.status = "sent"
        event.sent_at = utcnow()
        event.provider_message_id = str(response.json().get("id", ""))[:255] or None
        event.last_error = None
    except requests.RequestException as error:
        event.status = "failed"
        event.last_error = type(error).__name__
        current_app.logger.warning("Email delivery failed for outbox event %s", event.id)
    db.session.commit()
    return event


def retry_pending_outbox(limit=100):
    events = (
        db.session.query(EmailOutboxEvent)
        .filter(EmailOutboxEvent.status.in_(["pending", "failed"]))
        .order_by(EmailOutboxEvent.created_at.asc())
        .limit(limit)
        .all()
    )
    for event in events:
        deliver_outbox_event(event)
    return len(events)
