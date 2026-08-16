"""Public pages, lead capture, newsletter lifecycle, and public API routes."""

from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

from flask import Blueprint, Response, abort, current_app, flash, jsonify, redirect, render_template, request, url_for

from .anti_abuse import honeypot_tripped, verify_turnstile
from .content import AUTHORS, BLOG_POSTS, COUNSEL_DESK, PAGE_META, SITE_LASTMOD_ISO
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
    "counsel": "main.counsels_desk",
    "contact": "main.contact",
    "privacy": "main.privacy",
    "disclaimer": "main.disclaimer",
    "analysis": "main.analysis",
    "law_explained": "main.law_explained",
    "judgment_explained": "main.judgment_explained",
}

PAGE_SCHEMA_TYPES = {
    "home": "WebPage",
    "about": "AboutPage",
    "blogs": "CollectionPage",
    "counsel": "CollectionPage",
    "contact": "ContactPage",
    "privacy": "WebPage",
    "disclaimer": "WebPage",
    "analysis": "CollectionPage",
    "law_explained": "CollectionPage",
    "judgment_explained": "CollectionPage",
}


def public_url(endpoint, **values):
    path = url_for(endpoint, **values)
    return f"{current_app.config['PUBLIC_BASE_URL'].rstrip('/')}{path}"


def organization_schema():
    home_url = public_url("main.home")
    return {
        "@type": "Organization",
        "@id": f"{home_url}#organization",
        "name": "LexNush",
        "alternateName": "LexNush Legal Journal",
        "url": home_url,
        "logo": {
            "@type": "ImageObject",
            "url": public_url("static", filename="logo.jpg"),
            "width": 1024,
            "height": 1024,
        },
        "email": "editor@lexnush.com",
        "sameAs": ["https://www.linkedin.com/company/thelexnush/"],
    }


def website_schema():
    home_url = public_url("main.home")
    return {
        "@type": "WebSite",
        "@id": f"{home_url}#website",
        "name": "LexNush",
        "alternateName": "LexNush Legal Journal",
        "url": home_url,
        "description": "Independent legal analysis of law, policy, institutions, business, technology, and public life.",
        "inLanguage": "en",
        "publisher": {"@id": f"{home_url}#organization"},
    }


def breadcrumb_schema(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": position, "name": name, "item": item}
            for position, (name, item) in enumerate(items, start=1)
        ],
    }


def page_meta(name):
    meta = dict(PAGE_META[name])
    current_url = public_url(PAGE_ENDPOINTS[name])
    home_url = public_url("main.home")
    breadcrumb_items = [("Home", home_url)]
    if name != "home":
        breadcrumb_items.append((meta["title"].split(" | ", 1)[0], current_url))
    meta["url"] = current_url
    meta["image"] = public_url("static", filename="images/supreme-court-hero.jpg")
    meta["image_alt"] = "Supreme Court of India"
    meta["image_width"] = 1704
    meta["image_height"] = 923
    page_node = {
        "@type": PAGE_SCHEMA_TYPES[name],
        "@id": f"{current_url}#webpage",
        "url": current_url,
        "name": meta["title"],
        "description": meta["description"],
        "isPartOf": {"@id": f"{home_url}#website"},
        "about": {"@id": f"{home_url}#organization"},
        "inLanguage": "en",
    }
    graph = [website_schema(), organization_schema(), page_node, breadcrumb_schema(breadcrumb_items)]
    if name in {"home", "blogs"} and BLOG_POSTS:
        graph.append(
            {
                "@type": "ItemList",
                "@id": f"{current_url}#articles",
                "name": "LexNush legal analysis",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": position,
                        "url": public_url("main.post_detail", slug=post["slug"]),
                        "name": post["title"],
                    }
                    for position, post in enumerate(BLOG_POSTS, start=1)
                ],
            }
        )
    meta["schema"] = {
        "@context": "https://schema.org",
        "@graph": graph,
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


@main_bp.route("/analysis/")
def analysis():
    return render_template("section_page.html", section="analysis", meta=page_meta("analysis"))


@main_bp.route("/law-explained/")
def law_explained():
    return render_template("section_page.html", section="law_explained", meta=page_meta("law_explained"))


@main_bp.route("/judgment-explained/")
def judgment_explained():
    return render_template("section_page.html", section="judgment_explained", meta=page_meta("judgment_explained"))


@main_bp.route("/blogs/<slug>")
def post_detail(slug):
    post = find_post(slug)
    if post is None:
        abort(404)
    home_url = public_url("main.home")
    article_url = public_url("main.post_detail", slug=post["slug"])
    author_url = public_url("main.author_detail", slug=post["author_slug"])
    image_url = public_url("static", filename="images/lexnush-hero-editorial-1200.jpg")
    meta = {
        "title": f"{post['title']} | LexNush",
        "description": post["seo_description"],
        "type": "article",
        "url": article_url,
        "image": image_url,
        "image_alt": post["image_alt"],
        "image_width": 1200,
        "image_height": 583,
        "published_time": post["date_published_iso"],
        "modified_time": post["date_modified_iso"],
        "section": post["category"],
        "author_name": post["author"],
        "schema": {
            "@context": "https://schema.org",
            "@graph": [
                website_schema(),
                organization_schema(),
                {
                    "@type": "BlogPosting",
                    "@id": f"{article_url}#article",
                    "url": article_url,
                    "headline": post["title"],
                    "description": post["seo_description"],
                    "datePublished": post["date_published_iso"],
                    "dateModified": post["date_modified_iso"],
                    "author": {
                        "@type": "Person",
                        "@id": f"{author_url}#person",
                        "name": post["author"],
                        "url": author_url,
                    },
                    "publisher": {"@id": f"{home_url}#organization"},
                    "mainEntityOfPage": {"@type": "WebPage", "@id": article_url},
                    "image": {
                        "@type": "ImageObject",
                        "url": image_url,
                        "width": 1200,
                        "height": 583,
                        "caption": post["image_alt"],
                    },
                    "articleSection": post["category"],
                    "keywords": post["keywords"],
                    "wordCount": post["word_count"],
                    "inLanguage": "en-IN",
                    "isAccessibleForFree": True,
                },
                breadcrumb_schema(
                    [
                        ("Home", home_url),
                        ("Journal", public_url("main.blogs")),
                        (post["title"], article_url),
                    ]
                ),
            ],
        },
    }
    return render_template("post.html", post=post, author=AUTHORS[post["author_slug"]], meta=meta)


@main_bp.route("/authors/<slug>/")
def author_detail(slug):
    author = AUTHORS.get(slug)
    if author is None:
        abort(404)
    author_url = public_url("main.author_detail", slug=slug)
    home_url = public_url("main.home")
    author_posts = [post for post in BLOG_POSTS if post.get("author_slug") == slug]
    image_url = public_url("static", filename=author["image"])
    meta = {
        "title": f"{author['name']} | Founder & Author at LexNush",
        "description": author["short_bio"],
        "url": author_url,
        "image": image_url,
        "image_alt": f"{author['name']}, {author['role']} at LexNush",
        "image_width": 760,
        "image_height": 1013,
        "schema": {
            "@context": "https://schema.org",
            "@graph": [
                website_schema(),
                organization_schema(),
                {
                    "@type": "ProfilePage",
                    "@id": f"{author_url}#profile",
                    "url": author_url,
                    "name": f"{author['name']} | LexNush",
                    "dateModified": SITE_LASTMOD_ISO,
                    "mainEntity": {
                        "@type": "Person",
                        "@id": f"{author_url}#person",
                        "name": author["name"],
                        "jobTitle": author["role"],
                        "description": author["short_bio"],
                        "url": author_url,
                        "image": image_url,
                        "sameAs": [author["same_as"]],
                        "worksFor": {"@id": f"{home_url}#organization"},
                    },
                },
                breadcrumb_schema([("Home", home_url), (author["name"], author_url)]),
            ],
        },
    }
    return render_template("author.html", author=author, posts=author_posts, meta=meta)


@main_bp.route("/counsels-desk/")
def counsels_desk():
    return render_template("counsels_desk.html", counsel_desk=COUNSEL_DESK, meta=page_meta("counsel"))


@main_bp.route("/interviews/")
def interviews_legacy_redirect():
    """Preserve the old public URL while consolidating the section name."""
    return redirect(url_for("main.counsels_desk"), code=301)


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


@main_bp.route("/disclaimer/")
def disclaimer():
    return render_template("disclaimer.html", meta=page_meta("disclaimer"))


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
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /api/",
            "Disallow: /healthz",
            "Disallow: /newsletter/",
            f"Sitemap: {public_url('main.sitemap_xml')}",
            f"Sitemap: {public_url('main.feed_xml')}",
            "",
        ]
    )
    return Response(body, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    urls = [
        (public_url("main.home"), SITE_LASTMOD_ISO, public_url("static", filename="images/supreme-court-hero.jpg")),
        (public_url("main.about"), SITE_LASTMOD_ISO, public_url("static", filename="images/anushka-760.jpg")),
        (public_url("main.blogs"), SITE_LASTMOD_ISO, None),
        (public_url("main.analysis"), SITE_LASTMOD_ISO, None),
        (public_url("main.law_explained"), SITE_LASTMOD_ISO, None),
        (public_url("main.judgment_explained"), SITE_LASTMOD_ISO, None),
        (public_url("main.counsels_desk"), SITE_LASTMOD_ISO, None),
        (public_url("main.contact"), SITE_LASTMOD_ISO, None),
        (public_url("main.privacy"), SITE_LASTMOD_ISO, None),
        (public_url("main.disclaimer"), SITE_LASTMOD_ISO, None),
    ]
    urls.extend(
        (
            public_url("main.author_detail", slug=author["slug"]),
            SITE_LASTMOD_ISO,
            public_url("static", filename=author["image"]),
        )
        for author in AUTHORS.values()
    )
    urls.extend(
        (
            public_url("main.post_detail", slug=post["slug"]),
            post["date_modified_iso"].split("T", 1)[0],
            public_url("static", filename="images/lexnush-hero-editorial-1200.jpg"),
        )
        for post in BLOG_POSTS
    )
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for url, lastmod, image_url in urls:
        extra = f"<lastmod>{xml_escape(lastmod)}</lastmod>" if lastmod else ""
        image = f"<image:image><image:loc>{xml_escape(image_url)}</image:loc></image:image>" if image_url else ""
        body.append(f"  <url><loc>{xml_escape(url)}</loc>{extra}{image}</url>")
    body.append("</urlset>")
    return Response("\n".join(body), mimetype="application/xml")


@main_bp.route("/feed.xml")
def feed_xml():
    home_url = public_url("main.home")
    feed_updated = max(
        (post["date_modified_iso"] for post in BLOG_POSTS),
        default=f"{SITE_LASTMOD_ISO}T00:00:00+05:30",
    )
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        "  <title>LexNush Journal</title>",
        f"  <id>{xml_escape(home_url)}</id>",
        f'  <link href="{xml_escape(public_url("main.feed_xml"))}" rel="self"/>',
        f'  <link href="{xml_escape(home_url)}"/>',
        f"  <updated>{xml_escape(feed_updated)}</updated>",
        "  <subtitle>Clear, source-led analysis of law, policy, institutions, and public life.</subtitle>",
    ]
    for post in BLOG_POSTS:
        article_url = public_url("main.post_detail", slug=post["slug"])
        body.extend(
            [
                "  <entry>",
                f"    <title>{xml_escape(post['title'])}</title>",
                f"    <id>{xml_escape(article_url)}</id>",
                f'    <link href="{xml_escape(article_url)}"/>',
                f"    <published>{xml_escape(post['date_published_iso'])}</published>",
                f"    <updated>{xml_escape(post['date_modified_iso'])}</updated>",
                f"    <author><name>{xml_escape(post['author'])}</name></author>",
                f"    <summary>{xml_escape(post['seo_description'])}</summary>",
                "  </entry>",
            ]
        )
    body.append("</feed>")
    return Response("\n".join(body), mimetype="application/atom+xml")


@main_bp.app_errorhandler(400)
@main_bp.app_errorhandler(404)
@main_bp.app_errorhandler(429)
def client_error(error):
    meta = {
        "title": f"{error.code} | LexNush",
        "description": "The requested LexNush page could not be completed.",
        "robots": "noindex, follow",
    }
    return render_template("error.html", error=error, meta=meta), error.code


@main_bp.app_errorhandler(500)
def server_error(error):
    meta = {
        "title": "Server Error | LexNush",
        "description": "LexNush could not complete the request.",
        "robots": "noindex, follow",
    }
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
    for counsel in COUNSEL_DESK:
        haystack = f"{counsel['guest']} {counsel['title']} {counsel['role']}".lower()
        if query in haystack:
            results.append({"type": "Counsel’s Desk", "title": f"Counsel’s Desk: {counsel['guest']}", "summary": counsel["title"], "url": url_for("main.counsels_desk")})
    return jsonify(results[:8])
