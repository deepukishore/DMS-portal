import unittest
from pathlib import Path


class HomeNavigationButtonTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.templates = project_root / "templates"

    def test_authenticated_headers_offer_dashboard_home_navigation(self):
        for template_name in ("layout.html", "approval_review.html", "document_view.html"):
            with self.subTest(template=template_name):
                template = (self.templates / template_name).read_text(encoding="utf-8")
                self.assertIn('class="btn-page-home"', template)
                self.assertIn('aria-label="Go to dashboard"', template)
                self.assertIn("url_for('dashboard.index')", template)

    def test_shared_header_hides_redundant_home_button_on_dashboard(self):
        layout = (self.templates / "layout.html").read_text(encoding="utf-8")
        self.assertIn("{% if request.endpoint != 'dashboard.index' %}", layout)

    def test_public_authentication_pages_do_not_link_to_dashboard(self):
        for template_name in ("register.html", "reset_password.html"):
            with self.subTest(template=template_name):
                template = (self.templates / "auth" / template_name).read_text(
                    encoding="utf-8"
                )
                self.assertNotIn('class="btn-page-home"', template)


if __name__ == "__main__":
    unittest.main()
