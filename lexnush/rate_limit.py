from collections import defaultdict
import time

from flask import request


RATE_LIMIT_BUCKETS = defaultdict(list)


def client_identifier():
    # ProxyFix normalizes this value when trusted proxies are configured. Reading
    # X-Forwarded-For directly would let any client select its own rate-limit key.
    remote_addr = request.remote_addr or "unknown"
    return f"{remote_addr}:{request.endpoint or request.path}"


def is_rate_limited(scope, limit, window_seconds):
    now = time.monotonic()
    key = f"{scope}:{client_identifier()}"
    bucket = RATE_LIMIT_BUCKETS[key]
    bucket[:] = [stamp for stamp in bucket if now - stamp < window_seconds]
    if len(bucket) >= limit:
        return True
    bucket.append(now)
    return False


def clear_rate_limits():
    RATE_LIMIT_BUCKETS.clear()
