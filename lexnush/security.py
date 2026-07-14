import secrets

from flask import abort, current_app, request, session

from .rate_limit import is_rate_limited

try:
    from flask_talisman import Talisman
except ImportError:  # pragma: no cover - exercised only when dependency is installed
    Talisman = None

try:
    from flask_wtf.csrf import CSRFProtect, generate_csrf
except ImportError:  # pragma: no cover - exercised only when dependency is installed
    CSRFProtect = None
    generate_csrf = None


CSP = {
    "default-src": "'self'",
    "base-uri": "'self'",
    "connect-src": "'self'",
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "form-action": "'self'",
    "frame-ancestors": "'none'",
    "img-src": ["'self'", "data:"],
    "media-src": "'none'",
    "object-src": "'none'",
    "script-src": "'self'",
    "style-src": ["'self'", "https://fonts.googleapis.com"],
    "worker-src": "'none'",
}


def fallback_csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_fallback_csrf():
    expected = session.get("_csrf_token", "")
    submitted = request.form.get("_csrf_token", "") or request.headers.get("X-CSRF-Token", "")
    if not expected or not submitted or not secrets.compare_digest(expected, submitted):
        abort(400)


def csp_header_value():
    parts = []
    for directive, value in CSP.items():
        values = value if isinstance(value, list) else [value]
        parts.append(f"{directive} {' '.join(values)}")
    return "; ".join(parts)


def init_security(app):
    if CSRFProtect and app.config.get("WTF_CSRF_ENABLED", True):
        CSRFProtect(app)
        app.context_processor(lambda: {"csrf_token": generate_csrf})
    else:
        app.context_processor(lambda: {"csrf_token": fallback_csrf_token})

        @app.before_request
        def fallback_csrf_protect():
            if request.method == "POST":
                validate_fallback_csrf()

    @app.before_request
    def protect_form_posts():
        if request.method == "POST":
            limit, window = current_app.config["RATE_LIMIT_FORMS"]
            if is_rate_limited("form-post", limit=limit, window_seconds=window):
                abort(429)

    if Talisman:
        Talisman(
            app,
            content_security_policy=CSP,
            content_security_policy_nonce_in=[],
            force_https=app.config["SESSION_COOKIE_SECURE"],
            frame_options="DENY",
            permissions_policy="camera=(), geolocation=(), microphone=()",
            referrer_policy="strict-origin-when-cross-origin",
            session_cookie_http_only=True,
            session_cookie_secure=app.config["SESSION_COOKIE_SECURE"],
            strict_transport_security=app.config["SESSION_COOKIE_SECURE"],
            strict_transport_security_include_subdomains=True,
        )
    else:
        pass

    # Talisman supplies the core policy when installed. These headers and the
    # no-store HTML policy are applied in both modes to keep behavior identical.
    app.after_request(apply_security_headers)


def apply_security_headers(response):
    response.headers.setdefault("Content-Security-Policy", csp_header_value())
    response.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=()")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-XSS-Protection", "0")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    if response.mimetype == "text/html":
        response.headers.setdefault("Cache-Control", "no-store, max-age=0")
    if current_app.config["SESSION_COOKIE_SECURE"]:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response
