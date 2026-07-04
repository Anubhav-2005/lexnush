from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from .content import BLOG_POSTS, INTERVIEWS, PAGE_META
from .db import save_contact_submission, save_newsletter_signup
from .rate_limit import is_rate_limited
from .validators import normalize_text, validate_contact_form, validate_email


main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")


def page_meta(name):
    return PAGE_META[name]


def find_post(slug):
    return next((item for item in BLOG_POSTS if item["slug"] == slug), None)


@main_bp.route("/")
def home():
    featured = BLOG_POSTS[0] if BLOG_POSTS else None
    return render_template("index.html", featured_post=featured, meta=page_meta("home"))


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
    meta = {
        "title": post["title"],
        "description": post["summary"],
        "type": "article",
    }
    return render_template("post.html", post=post, meta=meta)


@main_bp.route("/interviews/")
def interviews():
    return render_template("interviews.html", interviews=INTERVIEWS, meta=page_meta("interviews"))


@main_bp.route("/contact/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        form_data, errors = validate_contact_form(request.form)

        if errors:
            flash("Please review the highlighted fields.", "error")
            return render_template(
                "contact.html",
                form_data=form_data,
                errors=errors,
                meta=page_meta("contact"),
            ), 400

        save_contact_submission(
            form_data["name"],
            form_data["email"],
            form_data["topic"],
            form_data["message"],
        )
        flash("Thank you. Your message has been received.", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html", form_data={}, errors={}, meta=page_meta("contact"))


@main_bp.route("/newsletter/", methods=["POST"])
def newsletter_signup():
    email, error = validate_email(request.form.get("email"))
    if error:
        flash(error, "error")
        return redirect(url_for("main.blogs"))

    save_newsletter_signup(email)
    flash("You are on the LexNush journal list.", "success")
    return redirect(url_for("main.blogs"))


@main_bp.route("/healthz")
def healthz():
    return jsonify({"service": "lexnush", "status": "ok"})


@main_bp.route("/robots.txt")
def robots_txt():
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {url_for('main.sitemap_xml', _external=True)}",
            "",
        ]
    )
    return Response(body, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    urls = [
        url_for("main.home", _external=True),
        url_for("main.about", _external=True),
        url_for("main.blogs", _external=True),
        url_for("main.interviews", _external=True),
        url_for("main.contact", _external=True),
    ]
    urls.extend(url_for("main.post_detail", slug=post["slug"], _external=True) for post in BLOG_POSTS)
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    body.extend(f"  <url><loc>{url}</loc></url>" for url in urls)
    body.append("</urlset>")
    return Response("\n".join(body), mimetype="application/xml")


@main_bp.app_errorhandler(400)
@main_bp.app_errorhandler(404)
@main_bp.app_errorhandler(429)
def client_error(error):
    meta = {
        "title": f"{error.code} | LexNush",
        "description": "The requested LexNush page could not be completed.",
    }
    return render_template("error.html", error=error, meta=meta), error.code


@main_bp.app_errorhandler(500)
def server_error(error):
    meta = {
        "title": "Server Error | LexNush",
        "description": "LexNush could not complete the request.",
    }
    return render_template("error.html", error=error, meta=meta), 500


@api_bp.route("/search")
def search():
    limit, window = current_app.config["RATE_LIMIT_SEARCH"]
    if is_rate_limited("search", limit=limit, window_seconds=window):
        abort(429)

    query = normalize_text(request.args.get("q"), 80).lower()
    if len(query) < 2:
        return jsonify([])

    results = []
    for post in BLOG_POSTS:
        haystack = f"{post['title']} {post['summary']} {post['category']}".lower()
        if query in haystack:
            results.append(
                {
                    "type": "Article",
                    "title": post["title"],
                    "summary": post["summary"],
                    "url": url_for("main.post_detail", slug=post["slug"]),
                }
            )

    for interview in INTERVIEWS:
        haystack = f"{interview['guest']} {interview['title']} {interview['role']}".lower()
        if query in haystack:
            results.append(
                {
                    "type": "Interview",
                    "title": f"Interview: {interview['guest']}",
                    "summary": interview["title"],
                    "url": url_for("main.interviews"),
                }
            )

    return jsonify(results[:8])
