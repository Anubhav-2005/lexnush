# LexNush deployment checklist

Follow this checklist in order. Do not add real visitor data until every P0 item is complete.

## 1. Create accounts and services

- [ ] Create a Render web service, managed Postgres database, and Key Value instance in the same region.
- [ ] Keep the Key Value instance private (`ipAllowList: []`) and use its internal authenticated connection URL for `REDIS_URL`.
- [ ] Create a Resend account, verify the sending domain, and configure SPF/DKIM. Add a DMARC record when the domain policy is ready.
- [ ] Create a Sentry project for Flask and copy its DSN.
- [ ] Optionally create a Cloudflare Turnstile widget for public form bot protection.

## 2. Generate secrets locally

```sh
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
python3 -c "from argon2 import PasswordHasher; import getpass; print(PasswordHasher().hash(getpass.getpass('Admin password: ')))"
```

Store the generated values only in Render's encrypted environment-variable interface or a secret manager. Never paste them into Git, source code, issue trackers, or browser screenshots.

## 3. Set required Render environment variables

| Variable | Required value |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | New 48+ byte random value |
| `DATABASE_URL` | Render Postgres internal connection string |
| `REDIS_URL` | Render Key Value internal connection string, preferably authenticated |
| `PUBLIC_BASE_URL` | `https://your-real-domain.example` |
| `LEXNUSH_TRUSTED_HOSTS` | `your-real-domain.example,www.your-real-domain.example` as applicable |
| `TRUSTED_PROXY_COUNT` | Confirmed count for the Render proxy topology; start with `1` only after verifying Render setup |
| `RESEND_API_KEY` | Resend production API key |
| `MAIL_FROM` | Verified sender, e.g. `LexNush <hello@your-real-domain.example>` |
| `CONTACT_RECIPIENT_EMAIL` | Owner inbox that handles leads |
| `ADMIN_EMAIL` | The sole initial staff email |
| `ADMIN_PASSWORD_HASH` | Argon2 hash generated above |
| `SENTRY_DSN` | Sentry Flask DSN |

Optional: `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY`, `TURNSTILE_REQUIRED=true`, `DATA_RETENTION_DAYS=365`.

## 4. Deploy and verify

- [ ] Run `flask --app app db upgrade` in the Render build step before starting Gunicorn.
- [ ] Confirm `/healthz` returns `200`.
- [ ] Visit the custom HTTPS domain; test `http` to HTTPS redirect, one canonical host, navigation, 404, robots, sitemap, and metadata.
- [ ] Submit a contact form using a safe test address. Confirm the database record, owner email, Resend delivery record, and admin dashboard entry.
- [ ] Subscribe with a safe test address; confirm double opt-in works and an unconfirmed address remains `pending`.
- [ ] Sign in at `/admin/login/`, verify access to leads, logout, and verify anonymous access is rejected.
- [ ] Trigger a harmless test exception only in a preview environment and confirm Sentry captures it without form contents.
- [ ] Run a backup and restore it into a non-production database. Record the date and result.

## 5. DNS and launch

- [ ] Add the Render custom-domain records exactly as shown in the Render dashboard.
- [ ] Set one canonical host and redirect the alternative host.
- [ ] Enable Resend domain records before sending public email.
- [ ] Submit `https://your-real-domain.example/sitemap.xml` in Google Search Console and Bing Webmaster Tools.
- [ ] Ensure the privacy page and contact address are correct for your business/jurisdiction.

Render Blueprints support Postgres and Key Value connection-string references, and Render recommends internal Key Value URLs for colocated services. Verify the current Blueprint schema before applying it. [Render Blueprint reference](https://render.com/docs/blueprint-spec), [Render Key Value guide](https://render.com/docs/key-value).
