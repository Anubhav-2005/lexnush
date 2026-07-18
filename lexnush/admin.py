"""Protected operational dashboard for a single configured administrator."""

import csv
import io

from flask import Blueprint, Response, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_, select

from .auth import ConfigAdmin, verify_admin_password
from .db import ContactSubmission, EmailOutboxEvent, NewsletterSubscription, audit_admin_action, db, utcnow
from .rate_limit import hashed_client_ip, limiter

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def dashboard_meta(title):
    return {"title": f"{title} | LexNush Admin", "description": "Protected LexNush operations."}


def safe_csv_cell(value):
    value = "" if value is None else str(value)
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value


@admin_bp.route("/login/", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["RATE_LIMIT_LOGIN"], methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if email == current_app.config["ADMIN_EMAIL"] and verify_admin_password(password):
            login_user(ConfigAdmin(email), remember=False, fresh=True)
            audit_admin_action(email, "login", ip_hash=hashed_client_ip())
            db.session.commit()
            return redirect(url_for("admin.dashboard"))
        audit_admin_action(email or "unknown", "login_failed", ip_hash=hashed_client_ip())
        db.session.commit()
        flash("Sign-in failed.", "error")
    return render_template("admin_login.html", meta=dashboard_meta("Sign in"))


@admin_bp.route("/logout/", methods=["POST"])
@login_required
def logout():
    audit_admin_action(current_user.email, "logout", ip_hash=hashed_client_ip())
    db.session.commit()
    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    return render_template(
        "admin_dashboard.html",
        contacts=db.session.query(ContactSubmission).count(),
        pending_contacts=db.session.query(ContactSubmission).filter_by(status="new").count(),
        pending_subscribers=db.session.query(NewsletterSubscription).filter_by(status="pending").count(),
        confirmed_subscribers=db.session.query(NewsletterSubscription).filter_by(status="confirmed").count(),
        sent_emails=db.session.query(EmailOutboxEvent).filter_by(status="sent").count(),
        attention_emails=db.session.query(EmailOutboxEvent).filter(EmailOutboxEvent.status.in_(["pending", "failed"])).count(),
        recent_contacts=db.session.scalars(select(ContactSubmission).order_by(ContactSubmission.created_at.desc()).limit(6)).all(),
        recent_emails=db.session.scalars(select(EmailOutboxEvent).order_by(EmailOutboxEvent.created_at.desc()).limit(6)).all(),
        meta=dashboard_meta("Dashboard"),
    )


@admin_bp.route("/contacts/")
@login_required
def contacts():
    page = max(1, request.args.get("page", 1, type=int))
    query = (request.args.get("q") or "").strip()[:120]
    statement = select(ContactSubmission).order_by(ContactSubmission.created_at.desc())
    if query:
        pattern = f"%{query}%"
        statement = statement.where(
            or_(ContactSubmission.name.ilike(pattern), ContactSubmission.email.ilike(pattern), ContactSubmission.topic.ilike(pattern))
        )
    contacts_page = db.paginate(statement, page=page, per_page=25, max_per_page=100)
    return render_template("admin_contacts.html", contacts_page=contacts_page, query=query, meta=dashboard_meta("Inquiries"))


@admin_bp.route("/contacts/<int:contact_id>/status", methods=["POST"])
@login_required
def update_contact_status(contact_id):
    contact = db.get_or_404(ContactSubmission, contact_id)
    status = request.form.get("status")
    if status not in {"new", "reviewed", "replied"}:
        abort(400)
    contact.status = status
    if status == "reviewed" and not contact.reviewed_at:
        contact.reviewed_at = utcnow()
    if status == "replied":
        contact.replied_at = utcnow()
        contact.reviewed_at = contact.reviewed_at or utcnow()
    audit_admin_action(current_user.email, "contact_status_updated", "contact", contact.id, hashed_client_ip())
    db.session.commit()
    flash("Inquiry status updated.", "success")
    return redirect(url_for("admin.contacts"))


@admin_bp.route("/subscribers/")
@login_required
def subscribers():
    page = max(1, request.args.get("page", 1, type=int))
    statement = select(NewsletterSubscription).order_by(NewsletterSubscription.created_at.desc())
    subscribers_page = db.paginate(statement, page=page, per_page=25, max_per_page=100)
    return render_template("admin_subscribers.html", subscribers_page=subscribers_page, meta=dashboard_meta("Subscribers"))


@admin_bp.route("/emails/")
@login_required
def emails():
    page = max(1, request.args.get("page", 1, type=int))
    status = (request.args.get("status") or "all").strip().lower()
    allowed_statuses = {"all", "pending", "sent", "failed"}
    if status not in allowed_statuses:
        abort(400)
    statement = select(EmailOutboxEvent).order_by(EmailOutboxEvent.created_at.desc())
    if status != "all":
        statement = statement.where(EmailOutboxEvent.status == status)
    emails_page = db.paginate(statement, page=page, per_page=25, max_per_page=100)
    return render_template("admin_emails.html", emails_page=emails_page, status=status, meta=dashboard_meta("Email delivery"))


@admin_bp.route("/export/contacts.csv")
@login_required
def export_contacts():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "name", "email", "topic", "status", "created_at"])
    for contact in db.session.scalars(select(ContactSubmission).order_by(ContactSubmission.created_at.desc())):
        writer.writerow([safe_csv_cell(contact.id), safe_csv_cell(contact.name), safe_csv_cell(contact.email), safe_csv_cell(contact.topic), contact.status, contact.created_at.isoformat()])
    audit_admin_action(current_user.email, "contacts_exported", ip_hash=hashed_client_ip())
    db.session.commit()
    return Response(buffer.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=lexnush-contacts.csv", "Cache-Control": "no-store"})
