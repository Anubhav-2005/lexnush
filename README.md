# LexNush

LexNush is a server-rendered Flask publication site with a production-oriented lead and newsletter workflow: PostgreSQL persistence, Redis-backed rate limiting, Resend email outbox delivery, double opt-in subscriptions, and a protected single-operator dashboard.

## What is included

- Flask app factory, blueprints, server-rendered Jinja pages, search, SEO metadata, robots and sitemap.
- SQLAlchemy models and Alembic migrations for contacts, newsletters, tokens, email outbox events, and admin audit events.
- Contact notifications stored in an outbox before delivery is attempted, so a provider failure does not lose the inquiry.
- Newsletter double opt-in and token-based unsubscribe lifecycle.
- Argon2-protected admin login at `/admin/login/`; no public registration exists.
- CSRF, Redis rate limiting, input validation, optional Turnstile, CSP, HSTS in production, trusted-host checks, secure cookies, and structured PII-redacting logging.
- GitHub Actions checks for tests, Ruff, Bandit, dependency audit, and secret scanning.

## Local development

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a; . .env; set +a
python app.py
```

Local development uses SQLite and in-memory rate limits by default. Do not use those defaults for real visitor data.

## Database migrations

Use a fresh local database when applying the first migration:

```sh
flask --app app db upgrade
flask --app app db current
```

Development/tests can create their isolated SQLite schema automatically. On Render, the pre-deploy release phase runs `flask --app app db upgrade && flask --app app verify-production-database` against managed PostgreSQL before Gunicorn starts. The verifier rejects SQLite, missing tables, and an Alembic revision below head.

## Admin password

Generate an Argon2 password hash without writing the password to shell history:

```sh
python3 -c "from argon2 import PasswordHasher; import getpass; print(PasswordHasher().hash(getpass.getpass('Admin password: ')))"
```

Set the result as `ADMIN_PASSWORD_HASH`; set the matching `ADMIN_EMAIL` in the host secret manager. Never create a default admin account or commit a hash for a real password.

## Production environment

Production startup fails closed until these are configured:

```text
LEXNUSH_ENV=production
SECRET_KEY=<new high-entropy secret>
DATABASE_URL=<managed PostgreSQL connection string>
REDIS_URL=<managed Redis/Valkey connection string>
PUBLIC_BASE_URL=https://your-domain.example
LEXNUSH_TRUSTED_HOSTS=your-domain.example,www.your-domain.example
TRUSTED_PROXY_COUNT=1
RESEND_API_KEY=<Resend API key>
MAIL_FROM=LexNush <hello@your-domain.example>
CONTACT_RECIPIENT_EMAIL=owner@your-domain.example
ADMIN_EMAIL=owner@your-domain.example
ADMIN_PASSWORD_HASH=<Argon2 hash>
SENTRY_DSN=<Sentry DSN>
```

Optional bot protection:

```text
TURNSTILE_SITE_KEY=<Cloudflare site key>
TURNSTILE_SECRET_KEY=<Cloudflare secret key>
TURNSTILE_REQUIRED=true
DATA_RETENTION_DAYS=365
```

`TRUSTED_PROXY_COUNT` must match the actual number of trusted proxies in front of the app. Do not copy `1` blindly—verify it with the host’s current documentation.

## Operational commands

```sh
flask --app app retry-email-outbox --limit 100
flask --app app purge-personal-data --older-than-days 365
flask --app app verify-production-database
```

The first retries failed/pending Resend events. The second permanently removes old personal data, so run it only as part of a reviewed retention policy. The third is read-only and succeeds only on PostgreSQL with the complete current migration schema.

## Verification

```sh
python -m unittest discover -s tests
ruff check lexnush tests app.py wsgi.py
bandit -r lexnush -ll
pip-audit -r requirements.txt
```

## Deployment

`render.yaml` describes a Render web service, PostgreSQL, and private Key Value instance. Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) exactly before launch. Run a real contact, newsletter confirmation, admin-login, backup, restore, Sentry, and mobile verification on the deployed domain before accepting public leads.

## Backup, rollback, and recovery

- Use managed PostgreSQL backups and test a restore into a non-production database at least quarterly.
- Keep a prior Render deploy ready for rollback, but do not roll back database migrations without an explicit migration/recovery plan.
- A local SQLite backup command exists only for local development; it is not a production backup system.
- See [SECURITY_OPERATIONS.md](SECURITY_OPERATIONS.md) for the recurring security and incident process.
