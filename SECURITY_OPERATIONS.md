# Security operations

## Weekly

- Review Sentry errors and uptime alerts. Assign an owner to every recurring error.
- Review new contact inquiries and failed outbox events in `/admin/`.
- Check the Redis/Key Value service health and memory policy.

## Monthly

- Run `pip-audit -r requirements.txt`, review dependency updates, and merge tested security fixes.
- Review administrator access. Remove/rotate the password hash if the operator changes.
- Review rate-limit trends and public-form spam. Enable/adjust Turnstile if necessary.
- Check that privacy copy, retention period, contact recipient, and sender domain remain correct.

## Quarterly

- Perform a backup restore into a non-production PostgreSQL database and record the result.
- Rotate `SECRET_KEY`, Resend API key, and administrator password using a planned maintenance window. Rotating `SECRET_KEY` signs out active admin sessions.
- Review CSP, allowed third-party origins, and external dependencies.
- Run an accessibility/mobile regression pass and update browser support assumptions.

## Incident response

1. Preserve logs and Sentry event IDs. Do not paste contact messages into public tickets.
2. Stop the affected credential, sender key, or admin account if compromise is suspected.
3. Assess what data may have been accessed and consult appropriate legal/privacy advice for required notifications.
4. Restore service from a verified backup only after the root cause is understood.
5. Document the incident, corrective action, owner, and completion date.

## Data handling rules

- Do not export personal data unless necessary. CSV exports are protected against spreadsheet formula injection but remain sensitive data.
- Never log form bodies, passwords, API keys, or Resend credentials.
- Do not use Google Sheets as the system of record for inquiries.
- Retention purges are irreversible: test on non-production data first.
