"""Shared rate limiting backed by Redis in production."""

import hashlib

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def rate_limit_key():
    # ProxyFix only normalizes this after the configured trusted proxy count.
    return get_remote_address()


def hashed_client_ip():
    value = request.remote_addr or "unknown"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


limiter = Limiter(key_func=rate_limit_key, default_limits=[], headers_enabled=False)


def init_rate_limiting(app):
    limiter.init_app(app)
