import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import app
from lexnush.rate_limit import clear_rate_limits


class LexNushAppTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "lexnush-test.sqlite3"
        app.config.update(TESTING=True, DATABASE_PATH=str(self.database_path))
        clear_rate_limits()
        self.client = app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def csrf_from(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        match = re.search(r'name="_csrf_token" value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def test_public_pages_render(self):
        for path in ["/", "/about/", "/blogs/", "/interviews/", "/contact/", "/healthz"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_security_headers_are_present(self):
        response = self.client.get("/")
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["Referrer-Policy"], "strict-origin-when-cross-origin")
        self.assertIn("camera=()", response.headers["Permissions-Policy"])

    def test_search_returns_matching_posts(self):
        response = self.client.get("/api/search?q=arbitral")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["type"], "Article")
        self.assertIn("summary", data[0])

    def test_pages_include_structured_data(self):
        home = self.client.get("/").get_data(as_text=True)
        article = self.client.get("/blogs/surgery-or-autopsy-adr-award-modification").get_data(as_text=True)
        self.assertIn('"Organization"', home)
        self.assertIn('"BreadcrumbList"', home)
        self.assertIn('"Article"', article)
        self.assertIn('"Person"', article)

    def test_newsletter_rejects_external_return_url(self):
        token = self.csrf_from("/blogs/")
        response = self.client.post(
            "/newsletter/",
            data={"_csrf_token": token, "email": "reader@example.com", "next": "https://example.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/blogs/"))

    def test_templates_do_not_emit_inline_styles(self):
        for path in ["/", "/about/", "/blogs/", "/interviews/", "/contact/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertNotIn(b" style=", response.data)

    def test_contact_requires_csrf(self):
        response = self.client.post("/contact/", data={})
        self.assertEqual(response.status_code, 400)

    def test_contact_submission_is_persisted(self):
        token = self.csrf_from("/contact/")
        response = self.client.post(
            "/contact/",
            data={
                "_csrf_token": token,
                "name": "Asha Rao",
                "email": "asha@example.com",
                "topic": "Editorial pitch",
                "message": "I would like to share a detailed legal commentary proposal.",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your message has been received", response.data)

        connection = sqlite3.connect(self.database_path)
        rows = connection.execute("SELECT name, email, topic FROM contact_submissions").fetchall()
        connection.close()

        self.assertEqual(rows, [("Asha Rao", "asha@example.com", "Editorial pitch")])


if __name__ == "__main__":
    unittest.main()
