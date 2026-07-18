import json
import os
import re
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from lexnush import create_app, main_route_url, static_asset_url
from lexnush.admin import safe_csv_cell
from lexnush.config import normalize_trusted_hosts
from lexnush.db import ContactSubmission, EmailOutboxEvent, NewsletterSubscription, db, purge_personal_data, utcnow
from lexnush.security import sanitize_article_html


class LexNushAppTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        database_path = Path(self.tempdir.name) / "lexnush-test.sqlite3"
        self.app = create_app(
            "testing",
            {
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
                "PUBLIC_BASE_URL": "http://testserver",
                "CONTACT_RECIPIENT_EMAIL": "owner@example.test",
                "MAIL_FROM": "LexNush <hello@example.test>",
                "RESEND_API_KEY": "test-key",
                "RATELIMIT_STORAGE_URI": "memory://",
                "REDIS_URL": "memory://",
            },
        )
        with self.app.app_context():
            db.create_all()

        @self.app.route("/__test-server-error")
        def test_server_error():
            raise RuntimeError("controlled error")

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.tempdir.cleanup()

    def csrf_from(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        match = re.search(r'name="_csrf_token" value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def contact_payload(self, token=None):
        data = {
            "name": "Asha Rao",
            "email": "asha@example.com",
            "topic": "Editorial pitch",
            "message": "I would like to share a detailed legal commentary proposal.",
        }
        if token:
            data["_csrf_token"] = token
        return data

    def test_public_pages_render(self):
        for path in ["/", "/about/", "/blogs/", "/interviews/", "/contact/", "/privacy/", "/healthz"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_error_pages_render_with_static_asset_and_home_fallbacks(self):
        self.assertTrue(callable(self.app.jinja_env.globals["url_for"]))
        with self.app.app_context():
            self.assertEqual(static_asset_url("css/variables.css"), "/static/css/variables.css")
            self.assertEqual(main_route_url("main.home", "/"), "/")

        not_found = self.client.get("/does-not-exist")
        self.assertEqual(not_found.status_code, 404)
        self.assertIn(b'href="/static/css/variables.css', not_found.data)
        self.assertIn(b'href="/" class="outline-link">Return Home', not_found.data)

        self.app.config["PROPAGATE_EXCEPTIONS"] = False
        server_error = self.client.get("/__test-server-error")
        self.assertEqual(server_error.status_code, 500)
        self.assertIn(b'href="/static/css/variables.css', server_error.data)
        self.assertIn(b'href="/" class="outline-link">Return Home', server_error.data)

    def test_trusted_hosts_include_canonical_render_host_and_normalize_urls(self):
        hosts = normalize_trusted_hosts(
            ("https://preview.lexnush.onrender.com",),
            "https://lexnush.onrender.com",
        )
        self.assertEqual(hosts, ("preview.lexnush.onrender.com", "lexnush.onrender.com"))

    def test_public_ux_helpers_render_only_where_needed(self):
        article = self.client.get("/blogs/surgery-or-autopsy-adr-award-modification")
        self.assertIn(b"reading-progress-bar", article.data)
        self.assertNotIn(b"reading-progress-bar", self.client.get("/").data)
        contact = self.client.get("/contact/")
        self.assertIn(b'data-character-counter="message-counter"', contact.data)
        self.assertIn(b'maxlength="3000"', contact.data)

    def test_home_uses_editorial_dossier_without_redundant_final_cta(self):
        homepage = self.client.get("/")
        self.assertIn(b"LexNush dossier", homepage.data)
        self.assertIn(b"Our editorial approach", homepage.data)
        self.assertNotIn(b"dossier-orbit", homepage.data)
        self.assertNotIn(b"Indian law, explained", homepage.data)
        self.assertNotIn(b"Read law like it belongs in the real world.", homepage.data)

    def test_security_headers_and_canonical_url_are_present(self):
        response = self.client.get("/")
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("http://testserver/", response.get_data(as_text=True))

    def test_contact_is_persisted_with_outbox_event(self):
        response = self.client.post("/contact/", data=self.contact_payload(), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            contact = db.session.query(ContactSubmission).one()
            event = db.session.query(EmailOutboxEvent).one()
            self.assertEqual(contact.email, "asha@example.com")
            self.assertEqual(event.event_type, "contact-owner-notification")
            self.assertEqual(event.status, "pending")

    def test_contact_validation_and_honeypot(self):
        invalid = self.client.post("/contact/", data={"name": "A", "email": "nope", "topic": "x", "message": "short"})
        self.assertEqual(invalid.status_code, 400)
        bot = self.client.post("/contact/", data={**self.contact_payload(), "website": "spam.example"})
        self.assertEqual(bot.status_code, 400)

    def test_email_delivery_is_mockable_and_does_not_log_payload(self):
        self.app.config.update(EMAIL_DELIVERY_ENABLED=True)
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"id": "email_123"}
        with patch("lexnush.mailer.requests.post", return_value=response) as post:
            self.client.post("/contact/", data=self.contact_payload())
        self.assertTrue(post.called)
        with self.app.app_context():
            event = db.session.query(EmailOutboxEvent).one()
            self.assertEqual(event.status, "sent")
            self.assertEqual(event.provider_message_id, "email_123")

    def test_newsletter_requires_confirmation_before_confirmed(self):
        self.client.post("/newsletter/", data={"email": "reader@example.com", "next": "/blogs/"})
        with self.app.app_context():
            subscription = db.session.query(NewsletterSubscription).one()
            event = db.session.query(EmailOutboxEvent).one()
            self.assertEqual(subscription.status, "pending")
            signed_token = re.search(r'href="http://testserver(/newsletter/confirm/[^"]+)"', json.loads(event.payload_json)["html"]).group(1)
        confirmed = self.client.get(signed_token, follow_redirects=True)
        self.assertEqual(confirmed.status_code, 200)
        with self.app.app_context():
            self.assertEqual(db.session.query(NewsletterSubscription).one().status, "confirmed")

    def test_admin_requires_login_then_allows_operator(self):
        self.assertEqual(self.client.get("/admin/", follow_redirects=False).status_code, 302)
        login = self.client.post("/admin/login/", data={"email": "admin@example.test", "password": "test-admin-password"}, follow_redirects=True)
        self.assertEqual(login.status_code, 200)
        self.assertIn(b"Latest email activity", login.data)
        self.assertEqual(self.client.get("/admin/contacts/").status_code, 200)
        emails = self.client.get("/admin/emails/")
        self.assertEqual(emails.status_code, 200)
        self.assertIn(b"Email delivery ledger", emails.data)

    def test_admin_dashboard_and_email_ledger_show_database_activity(self):
        self.client.post("/contact/", data=self.contact_payload())
        self.client.post("/admin/login/", data={"email": "admin@example.test", "password": "test-admin-password"})

        dashboard = self.client.get("/admin/")
        self.assertIn(b"Total inquiries", dashboard.data)
        self.assertIn(b">1</strong><small>1 need review", dashboard.data)

        emails = self.client.get("/admin/emails/?status=pending")
        self.assertIn(b"New LexNush inquiry: Editorial pitch", emails.data)
        self.assertIn(b"owner@example.test", emails.data)
        attention = self.client.get("/admin/emails/?status=attention")
        self.assertEqual(attention.status_code, 200)
        self.assertIn(b"New LexNush inquiry: Editorial pitch", attention.data)

    def test_csv_formula_injection_is_neutralized(self):
        self.assertEqual(safe_csv_cell("=SUM(1,1)"), "'=SUM(1,1)")
        self.assertEqual(safe_csv_cell("normal@example.com"), "normal@example.com")

    def test_retention_purge_removes_old_records(self):
        with self.app.app_context():
            record = ContactSubmission(name="Old User", email="old@example.com", topic="Old", message="This is an old retained message.", created_at=utcnow() - timedelta(days=500))
            db.session.add(record)
            db.session.commit()
            contacts, subscribers = purge_personal_data(365)
            self.assertEqual((contacts, subscribers), (1, 0))

    def test_sanitizer_removes_script_and_event_handlers(self):
        cleaned = sanitize_article_html('<p onclick="alert(1)">Safe</p><script>alert(1)</script>')
        self.assertEqual(cleaned, "<p>Safe</p>alert(1)")

    def test_sitemap_and_robots_use_public_url(self):
        self.assertIn(b"http://testserver/sitemap.xml", self.client.get("/robots.txt").data)
        sitemap = self.client.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("<lastmod>2026-03-01</lastmod>", sitemap)
        self.assertIn("http://testserver/blogs/", sitemap)

    def test_csrf_is_enforced_when_enabled(self):
        secure_app = create_app(
            "testing",
            {
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{Path(self.tempdir.name) / 'csrf.sqlite3'}",
                "WTF_CSRF_ENABLED": True,
                "PUBLIC_BASE_URL": "http://testserver",
            },
        )
        with secure_app.app_context():
            db.create_all()
        response = secure_app.test_client().post("/contact/", data=self.contact_payload())
        self.assertEqual(response.status_code, 400)

    def test_production_config_fails_without_required_services(self):
        with self.assertRaises(RuntimeError):
            create_app("production", {"SECRET_KEY": "not-default", "DATABASE_URL": ""})

    def test_production_requires_postgresql_and_never_uses_sqlite_fallback(self):
        production_settings = {
            "SECRET_KEY": "not-default",
            "DATABASE_URL": "sqlite:////tmp/should-never-be-production.sqlite3",
            "REDIS_URL": "redis://cache.example.test:6379/0",
            "PUBLIC_BASE_URL": "https://lexnush.example.test",
            "TRUSTED_HOSTS": ["lexnush.example.test"],
            "RESEND_API_KEY": "test-key",
            "MAIL_FROM": "LexNush <hello@lexnush.example.test>",
            "CONTACT_RECIPIENT_EMAIL": "owner@lexnush.example.test",
            "ADMIN_EMAIL": "admin@lexnush.example.test",
            "ADMIN_PASSWORD_HASH": "$argon2id$test",
        }
        with self.assertRaisesRegex(RuntimeError, "PostgreSQL"):
            create_app("production", production_settings)

        production_settings["DATABASE_URL"] = "postgres://user:password@db.example.test:5432/lexnush"
        production_app = create_app("production", production_settings)
        self.assertEqual(
            production_app.config["SQLALCHEMY_DATABASE_URI"],
            "postgresql+psycopg://user:password@db.example.test:5432/lexnush",
        )

    def test_render_without_explicit_environment_fails_as_production(self):
        with patch.dict(os.environ, {"RENDER": "true", "LEXNUSH_ENV": "", "FLASK_ENV": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "DATABASE_URL"):
                create_app()

    def test_render_rejects_an_unknown_environment_instead_of_falling_back_to_sqlite(self):
        with patch.dict(os.environ, {"RENDER": "true", "LEXNUSH_ENV": "prod", "FLASK_ENV": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "Unsupported production environment"):
                create_app()

    def test_database_verification_command_rejects_sqlite(self):
        result = self.app.test_cli_runner().invoke(args=["verify-production-database"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Expected PostgreSQL", str(result.exception))


if __name__ == "__main__":
    unittest.main()
