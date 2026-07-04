from app import app

try:
    from flask_frozen import Freezer
except ImportError as exc:
    raise SystemExit(
        "Static export requires Frozen-Flask. The production app deploys with Gunicorn; "
        "install Frozen-Flask only if you still need a static snapshot."
    ) from exc

# Static snapshots are optional. The primary production target is the Flask app.
app.config["FREEZER_RELATIVE_URLS"] = True

freezer = Freezer(app)

if __name__ == "__main__":
    freezer.freeze()
