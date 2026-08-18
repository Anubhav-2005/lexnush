"""Production-only keepalive for Render's idle free web service instances."""

from threading import Event, Thread

import requests


def _ping_forever(app, url, interval, stop_event):
    """Make a low-cost inbound request before Render's 15-minute idle window."""
    while not stop_event.wait(interval):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "LexNush-Render-Keepalive/1.0"},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            app.logger.warning("Render keepalive request failed", exc_info=True)


def start_keepalive(app):
    """Start the optional Render keepalive thread exactly once per app process."""
    if not app.config.get("SELF_PING_ENABLED"):
        return None

    url = f"{app.config['PUBLIC_BASE_URL'].rstrip('/')}/healthz"
    interval = app.config["SELF_PING_INTERVAL_SECONDS"]
    stop_event = Event()
    thread = Thread(
        target=_ping_forever,
        args=(app, url, interval, stop_event),
        name="lexnush-render-keepalive",
        daemon=True,
    )
    thread.start()
    app.extensions["render_keepalive"] = {"thread": thread, "stop_event": stop_event}
    app.logger.info("Render keepalive enabled: pinging /healthz every %s seconds", interval)
    return thread
