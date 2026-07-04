# LexNush

LexNush is a Flask-powered premium legal publication with editorial pages, searchable posts, newsletter capture, contact submissions, and production security defaults.

## Project Structure

```text
lexnush/
  __init__.py        # app factory and blueprint registration
  config.py          # development/testing/production config
  content.py         # controlled editorial content seed data
  db.py              # SQLite schema and parameterized persistence
  rate_limit.py      # lightweight local rate limiting fallback
  routes.py          # page and API blueprints
  security.py        # CSRF, CSP, Talisman/WTF fallback security
  validators.py      # form normalization and validation
static/
  css/
    variables.css
    reset.css
    layout.css
    components.css
    pages.css
    responsive.css
  script.js
  theme.js
templates/
tests/
```

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

The app runs on `http://localhost:8000` by default.

If you want to load `.env` in a shell:

```bash
set -a
. .env
set +a
python app.py
```

## Production Environment

Set these variables in production:

```bash
FLASK_ENV=production
SECRET_KEY=replace-with-a-long-random-secret
LEXNUSH_DATABASE_PATH=instance/lexnush.sqlite3
PORT=8000
```

`SECRET_KEY` is required in production. SQLite tables and indexes are created automatically when the app first touches the database.

## Run In Production

```bash
gunicorn wsgi:app
```

Platforms that support a `Procfile` can use the included file directly.

## Backend Behavior

- Public pages are served from the `main` blueprint.
- `/api/search` is served from the `api` blueprint.
- Contact submissions are validated server-side and stored in SQLite.
- Newsletter signups are validated server-side and stored uniquely by email.
- Search is case-insensitive, debounced client-side, rate-limited server-side, and returns escaped JSON consumed through DOM APIs.
- `robots.txt`, `sitemap.xml`, canonical URLs, OpenGraph, Twitter cards, and schema microdata are included.

## Security Baseline

- `Flask-Talisman` is used when installed for CSP/security headers.
- `Flask-WTF` CSRF protection is used when installed.
- A fallback CSRF validator and security-header middleware keep local development safe even before optional extensions are installed.
- Secure, HttpOnly, SameSite cookies are configured, with secure cookies enabled in production.
- POST forms and search are rate-limited.
- Inputs are normalized and validated server-side.
- Database writes use parameterized SQL.
- `flask backup-db` creates timestamped SQLite backups under `instance/backups/`.
- Debug mode is disabled by production config.
- Branded 400/404/429/500 error pages are registered.

## Verification

```bash
python -m unittest discover -s tests
```
