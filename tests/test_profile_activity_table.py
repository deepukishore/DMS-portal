import unittest
from pathlib import Path


class ProfileActivityTableTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.template = (project_root / "templates" / "profile.html").read_text(
            encoding="utf-8"
        )
        self.styles = (project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )
        self.route = (project_root / "routes" / "profile_routes.py").read_text(
            encoding="utf-8"
        )

    def test_activity_table_has_stable_columns_and_semantic_timestamps(self):
        self.assertIn("profile-log-col-time", self.template)
        self.assertIn("profile-log-col-action", self.template)
        self.assertIn("profile-log-col-details", self.template)
        self.assertIn('<time datetime="{{ log.timestamp }}">', self.template)
        self.assertIn('aria-label="My activity logs"', self.template)

    def test_activity_table_wraps_details_without_horizontal_scrolling(self):
        self.assertIn(".profile-log-table .log-table", self.styles)
        self.assertIn("table-layout: fixed", self.styles)
        self.assertIn("overflow-x: hidden", self.styles)
        self.assertIn(".profile-log-details", self.styles)
        self.assertIn("overflow-wrap: anywhere", self.styles)

    def test_activity_logs_support_filters_and_pagination(self):
        for field in ("log_search", "log_action", "log_page", "log_page_size"):
            self.assertIn(field, self.route)
        self.assertIn('id="profile-log-search"', self.template)
        self.assertIn('id="profile-log-action"', self.template)
        self.assertIn('aria-label="Activity log pages"', self.template)
        self.assertIn("Page {{ log_page }} of {{ log_page_count }}", self.template)
        self.assertIn("profile-log-filters", self.styles)
        self.assertIn("profile-log-pagination", self.styles)


if __name__ == "__main__":
    unittest.main()
