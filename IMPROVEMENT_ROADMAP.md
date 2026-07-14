# Improvement roadmap

## 0–2 weeks: make lead capture safe

1. Move production data to managed PostgreSQL, or explicitly configure a persistent disk as a temporary single-instance measure.
2. Integrate Resend for contact-owner notifications and visitor acknowledgement; authenticate the sending domain (SPF/DKIM/DMARC as applicable).
3. Add a small protected staff workflow: initially a secure read-only admin page or CRM integration, with role-based access and audit logs.
4. Add Sentry, uptime checks, structured server logs that avoid message bodies, and an incident contact.
5. Add CI: tests, `pip-audit`, secret scanning, and dependency-update automation.
6. Publish a privacy notice, newsletter consent copy, double opt-in/unsubscribe workflow, and retention schedule.

## 2–6 weeks: strengthen quality and delivery

1. Convert large PNG/JPEG assets to responsive AVIF/WebP, fix the logo type/name, remove/blocking preloader, and verify Lighthouse on mobile.
2. Add Playwright/Cypress screenshots at 320, 360, 375, 390, 414, 768, 1024, and 1440 pixels.
3. Run axe-core and manual screen-reader/keyboard tests; add active-nav `aria-current` and table caption/scope.
4. Configure canonical domain redirects, explicit site URL, Search Console, sitemap `lastmod`, and social preview testing.
5. Populate Conversations or remove it from primary navigation until content is ready.
6. Add related posts, article archive/tag pages, editorial dates, author pages, and a content publishing workflow.

## 6–12 weeks: scale deliberately

1. Replace SQLite-backed rate-limit events with Redis or edge/WAF limits.
2. Add a proper content management system or secured internal editorial tooling; sanitize all user/editor HTML before rendering.
3. Introduce database migrations, staging deployment, feature flags where useful, performance budgets, and release checklists.
4. Add CRM lifecycle stages and reporting only when there is a real team/process to use them.

## Effort estimate

| Workstream | Estimated effort |
|---|---:|
| P0 production data, email, monitoring, CI | 24–40 hours |
| Privacy, responsive/a11y verification, performance | 16–28 hours |
| CMS/admin/Redis/scaling enhancements | 40–100+ hours |

**Near-term production readiness total:** roughly **40–68 hours**, assuming scope decisions are made quickly and no complex legal/CRM migration is required.

## Sequencing principle

Do not start with a polished admin dashboard. First ensure a real inquiry is durable, visible to an owner, replyable, protected, and recoverable. That gives the site a dependable business loop.
