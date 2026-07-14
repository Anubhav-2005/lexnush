"""Public pages, lead capture, newsletter lifecycle, and public API routes."""

from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

from flask import Blueprint, Response, abort, current_app, flash, jsonify, redirect, render_template, request, url_for

from .anti_abuse import honeypot_tripped, verify_turnstile
from .content import BLOG_POSTS, INTERVIEWS, PAGE_META
from .db import (
    consume_newsletter_token,
    create_newsletter_token,
    db,
    get_or_create_subscription,
    save_contact_submission,
    utcnow,
)
from .mailer import (
    deliver_outbox_event,
    queue_contact_notification,
    queue_newsletter_confirmation,
    queue_unsubscribe_confirmation,
    read_signed_newsletter_token,
    signed_newsletter_token,
)
from .rate_limit import limiter
from .security import sanitize_article_html
from .validators import normalize_text, validate_contact_form, validate_email

main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")

PAGE_ENDPOINTS = {
    "home": "main.home",
    "about": "main.about",
    "blogs": "main.blogs",
    "interviews": "main.interviews",
    "contact": "main.contact",
    "privacy": "main.privacy",
}


def public_url(endpoint, **values):
    path = url_for(endpoint, **values)
    return f"{current_app.config['PUBLIC_BASE_URL'].rstrip('/')}{path}"


def page_meta(name):
    meta = dict(PAGE_META[name])
    current_url = public_url(PAGE_ENDPOINTS[name])
    breadcrumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": public_url("main.home")}]
    if name != "home":
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": meta["title"], "item": current_url})
    meta["url"] = current_url
    meta["schema"] = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": "LexNush", "url": public_url("main.home"), "description": "Premium legal intelligence for clear, contextual analysis of Indian law."},
            {"@type": "Organization", "name": "LexNush", "url": public_url("main.home"), "email": "editor@lexnush.com", "sameAs": ["https://www.linkedin.com/company/thelexnush/"]},
            {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
        ],
    }
    return meta


def find_post(slug):
    post = next((item for item in BLOG_POSTS if item["slug"] == slug), None)
    if not post:
        return None
    safe_post = dict(post)
    safe_post["content"] = sanitize_article_html(post["content"])
    return safe_post


def safe_local_redirect(value, default_endpoint):
    target = (value or "").strip()
    parsed = urlsplit(target)
    if target.startswith("/") and not target.startswith("//") and not parsed.scheme and not parsed.netloc:
        return target
    return url_for(default_endpoint)


def form_antibot_error(form):
    if honeypot_tripped(form):
        # Bots receive no detail that helps them tune their attack.
        abort(400)
    if not verify_turnstile(form.get("cf-turnstile-response")):
        return "We could not verify your submission. Please try again."
    return None


@main_bp.route("/")
def home():
    featured = BLOG_POSTS[0] if BLOG_POSTS else None
    return render_template("index.html", featured_post=featured, posts=BLOG_POSTS[:3], meta=page_meta("home"))


@main_bp.route("/about/")
def about():
    return render_template("about.html", meta=page_meta("about"))


@main_bp.route("/blogs/")
def blogs():
    return render_template("blogs.html", posts=BLOG_POSTS, meta=page_meta("blogs"))


@main_bp.route("/blogs/<slug>")
def post_detail(slug):
    post = find_post(slug)
    if post is None:
        abort(404)
    article_url = public_url("main.post_detail", slug=post["slug"])
    meta = {
        "title": post["title"],
        "description": post["summary"],
        "type": "article",
        "url": article_url,
        "image": public_url("static", filename="images/lexnush-hero-editorial-1200.jpg"),
        "schema": {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Article", "headline": post["title"], "description": post["summary"], "datePublished": post["date_iso"], "dateModified": post["date_iso"], "author": {"@type": "Person", "name": post["author"]}, "publisher": {"@type": "Organization", "name": "LexNush"}, "mainEntityOfPage": article_url, "image": public_url("static", filename="images/lexnush-hero-editorial-1200.jpg")},
                {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": public_url("main.home")}, {"@type": "ListItem", "position": 2, "name": "Journal", "item": public_url("main.blogs")}, {"@type": "ListItem", "position": 3, "name": post["title"], "item": article_url}]},
            ],
        },
    }
    return render_template("post.html", post=post, meta=meta)


@main_bp.route("/interviews/")
def interviews():
    return render_template("interviews.html", interviews=INTERVIEWS, meta=page_meta("interviews"))


@main_bp.route("/contact/", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["RATE_LIMIT_CONTACT"], methods=["POST"])
def contact():
    if request.method == "POST":
        antibot_error = form_antibot_error(request.form)
        form_data, errors = validate_contact_form(request.form)
        if antibot_error:
            errors["form"] = antibot_error
        if errors:
            flash("Please review the highlighted fields.", "error")
            return render_template("contact.html", form_data=form_data, errors=errors, meta=page_meta("contact")), 400
        contact_submission = save_contact_submission(**form_data)
        event = queue_contact_notification(contact_submission)
        db.session.commit()
        deliver_outbox_event(event)
        flash("Thank you. Your message has been received. We aim to respond within 3–5 business days.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form_data={}, errors={}, meta=page_meta("contact"))


@main_bp.route("/newsletter/", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATE_LIMIT_NEWSLETTER"], methods=["POST"])
def newsletter_signup():
    target = safe_local_redirect(request.form.get("next"), "main.blogs")
    antibot_error = form_antibot_error(request.form)
    if antibot_error:
        flash(antibot_error, "error")
        return redirect(target)
    email, error = validate_email(request.form.get("email"))
    if error:
        flash(error, "error")
        return redirect(target)
    subscription = get_or_create_subscription(email)
    if subscription.status == "confirmed":
        db.session.commit()
        flash("That email is already confirmed for the LexNush journal list.", "success")
        return redirect(target)
    raw_token, _ = create_newsletter_token(subscription, "confirm")
    signed_token = signed_newsletter_token(subscription.id, raw_token, "confirm")
    event = queue_newsletter_confirmation(subscription, signed_token)
    db.session.commit()
    deliver_outbox_event(event)
    flash("Check your email to confirm your LexNush subscription.", "success")
    return redirect(target)


@main_bp.route("/newsletter/confirm/<signed_token>")
@limiter.limit(lambda: current_app.config["RATE_LIMIT_CONFIRM"])
def newsletter_confirm(signed_token):
    token_data = read_signed_newsletter_token(signed_token, "confirm")
    if not token_data:
        abort(400)
    subscription = consume_newsletter_token(token_data["token"], "confirm")
    if not subscription or subscription.id != token_data["subscription_id"]:
        abort(400)
    subscription.status = "confirmed"
    subscription.confirmed_at = subscription.confirmed_at or utcnow()
    db.session.commit()
    flash("Your subscription is confirmed. Welcome to the LexNush journal list.", "success")
    return redirect(url_for("main.blogs"))


@main_bp.route("/newsletter/unsubscribe/<signed_token>")
@limiter.limit(lambda: current_app.config["RATE_LIMIT_CONFIRM"])
def newsletter_unsubscribe(signed_token):
    token_data = read_signed_newsletter_token(signed_token, "unsubscribe")
    if not token_data:
        abort(400)
    subscription = consume_newsletter_token(token_data["token"], "unsubscribe")
    if not subscription or subscription.id != token_data["subscription_id"]:
        abort(400)
    subscription.status = "unsubscribed"
    subscription.unsubscribed_at = utcnow()
    event = queue_unsubscribe_confirmation(subscription)
    db.session.commit()
    deliver_outbox_event(event)
    flash("You have been unsubscribed.", "success")
    return redirect(url_for("main.home"))


@main_bp.route("/privacy/")
def privacy():
    return render_template("privacy.html", meta=page_meta("privacy"))


@main_bp.route("/healthz")
def healthz():
    try:
        db.session.execute(db.select(1))
    except Exception:
        current_app.logger.exception("Health check database failure")
        return jsonify({"service": "lexnush", "status": "degraded"}), 503
    return jsonify({"service": "lexnush", "status": "ok"})


@main_bp.route("/robots.txt")
def robots_txt():
    body = "\n".join(["User-agent: *", "Allow: /", f"Sitemap: {public_url('main.sitemap_xml')}", ""])
    return Response(body, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    urls = [(public_url("main.home"), None), (public_url("main.about"), None), (public_url("main.blogs"), None), (public_url("main.interviews"), None), (public_url("main.contact"), None)]
    urls.extend((public_url("main.post_detail", slug=post["slug"]), post["date_iso"]) for post in BLOG_POSTS)
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lastmod in urls:
        extra = f"<lastmod>{xml_escape(lastmod)}</lastmod>" if lastmod else ""
        body.append(f"  <url><loc>{xml_escape(url)}</loc>{extra}</url>")
    body.append("</urlset>")
    return Response("\n".join(body), mimetype="application/xml")


@main_bp.app_errorhandler(400)
@main_bp.app_errorhandler(404)
@main_bp.app_errorhandler(429)
def client_error(error):
    meta = {"title": f"{error.code} | LexNush", "description": "The requested LexNush page could not be completed."}
    return render_template("error.html", error=error, meta=meta), error.code


@main_bp.app_errorhandler(500)
def server_error(error):
    meta = {"title": "Server Error | LexNush", "description": "LexNush could not complete the request."}
    return render_template("error.html", error=error, meta=meta), 500


@api_bp.route("/search")
@limiter.limit(lambda: current_app.config["RATE_LIMIT_SEARCH"])
def search():
    query = normalize_text(request.args.get("q"), 80).lower()
    if len(query) < 2:
        return jsonify([])
    results = []
    for post in BLOG_POSTS:
        haystack = f"{post['title']} {post['summary']} {post['category']}".lower()
        if query in haystack:
            results.append({"type": "Article", "title": post["title"], "summary": post["summary"], "url": url_for("main.post_detail", slug=post["slug"])})
    for interview in INTERVIEWS:
        haystack = f"{interview['guest']} {interview['title']} {interview['role']}".lower()
        if query in haystack:
            results.append({"type": "Interview", "title": f"Interview: {interview['guest']}", "summary": interview["title"], "url": url_for("main.interviews")})
    return jsonify(results[:8])
