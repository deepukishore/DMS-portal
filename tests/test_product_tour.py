import unittest
from pathlib import Path


class ProductTourTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.layout = (project_root / "templates" / "layout.html").read_text(
            encoding="utf-8"
        )
        self.sidebar = (
            project_root / "templates" / "components" / "sidebar.html"
        ).read_text(encoding="utf-8")
        self.tour_component = (
            project_root / "templates" / "components" / "product_tour.html"
        ).read_text(encoding="utf-8")
        self.dashboard = (project_root / "templates" / "dashboard.html").read_text(
            encoding="utf-8"
        )
        self.document_view = (
            project_root / "templates" / "document_view.html"
        ).read_text(encoding="utf-8")
        self.approval_review = (
            project_root / "templates" / "approval_review.html"
        ).read_text(encoding="utf-8")
        self.auth_templates = [
            (project_root / "templates" / "auth" / name).read_text(encoding="utf-8")
            for name in ("login.html", "register.html", "reset_password.html")
        ]
        self.script = (project_root / "static" / "js" / "product_tour.js").read_text(
            encoding="utf-8"
        )
        self.styles = (project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )

    def test_tour_has_spotlight_dialog_and_custom_labels(self):
        self.assertIn("components/product_tour.html", self.layout)
        self.assertIn('id="product-tour"', self.tour_component)
        self.assertEqual(
            self.tour_component.count("product-tour-backdrop product-tour-backdrop-"), 4
        )
        self.assertIn('class="product-tour-highlight"', self.tour_component)
        self.assertIn('role="dialog"', self.tour_component)
        self.assertIn('aria-modal="true"', self.tour_component)
        for label in ('next: "Next"', 'previous: "Previous"', 'finish: "Finish"'):
            self.assertIn(label, self.layout)

    def test_new_users_auto_start_and_tour_can_be_replayed(self):
        self.assertIn("welcome_is_new_user", self.layout)
        self.assertIn('id="product-tour-launch"', self.sidebar)
        self.assertIn("dms-product-tour-complete", self.script)
        self.assertIn("window.startProductTour", self.script)
        self.assertIn("function launchTour()", self.script)
        self.assertNotIn("sessionStorage.setItem", self.script)

    def test_every_authenticated_page_gets_a_contextual_tour(self):
        for endpoint in (
            "auth.login",
            "auth.register",
            "auth.reset_password",
            "upload.index",
            "approvals.index",
            "tracking.index",
            "document_library.index",
            "graphics_report.index",
            "revision_history.index",
            "archive.index",
            "system_log.index",
            "people.index",
            "profile.index",
            "notifications.portal_updates",
            "about.index",
            "about.about_track_docs",
            "customer_records.index",
            "plant_assets.index",
            "procedures.index",
            "procedures.sub_index",
            "approvals.review_document",
            "dashboard.view_document",
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIn(f"'{endpoint}'", self.script)
        self.assertIn("pageEndpoint.startsWith('categories.')", self.script)
        self.assertIn("genericPageSteps", self.script)

    def test_standalone_document_pages_include_tour_controls(self):
        for template in (self.document_view, self.approval_review):
            self.assertIn("components/product_tour.html", template)
            self.assertIn('id="product-tour-launch"', template)
            self.assertIn("pageEndpoint", template)
            self.assertIn("js/product_tour.js", template)

    def test_public_authentication_pages_have_manual_page_tours(self):
        for template in self.auth_templates:
            self.assertIn("components/product_tour.html", template)
            self.assertIn('id="product-tour-launch"', template)
            self.assertIn("pageEndpoint", template)
            self.assertIn("js/product_tour.js", template)

    def test_dashboard_exposes_all_tour_targets(self):
        for target in (
            'data-tour="library-overview"',
            'data-tour="quick-actions"',
            'data-tour="document-search"',
        ):
            self.assertIn(target, self.dashboard)
        self.assertIn('data-tour="main-navigation"', self.sidebar)
        self.assertIn('data-tour="app-header"', self.layout)
        self.assertIn('data-tour="notifications"', self.layout)

    def test_tour_auto_scrolls_and_repositions_the_spotlight(self):
        self.assertIn("scrollIntoView", self.script)
        self.assertIn("behavior: reducedMotion.matches ? 'auto' : 'smooth'", self.script)
        self.assertIn("window.addEventListener('scroll', schedulePosition, true)", self.script)
        self.assertIn(".product-tour-backdrop {", self.styles)
        self.assertIn("background: rgba(3, 12, 22, .72)", self.styles)


if __name__ == "__main__":
    unittest.main()
