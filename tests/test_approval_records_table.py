import unittest
from pathlib import Path


class ApprovalRecordsTableTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.template = (project_root / "templates" / "approvals.html").read_text(
            encoding="utf-8"
        )
        self.styles = (project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )

    def test_document_number_replaces_customer_column(self):
        self.assertIn("<th>Document Number</th>", self.template)
        self.assertIn("approval-col-document-number", self.template)
        self.assertIn("{{ r.document_number or '—' }}", self.template)
        self.assertNotIn("<th>Customer</th>", self.template)
        self.assertNotIn("approval-col-customer", self.template)
        self.assertNotIn("badge(r.customer", self.template)

    def test_search_and_records_share_one_panel(self):
        marker = '<section class="surface-panel approval-records-panel">'
        self.assertEqual(self.template.count(marker), 1)
        panel_start = self.template.index(marker)
        panel_end = self.template.index("</section>", panel_start)
        panel = self.template[panel_start:panel_end]

        self.assertIn("Approval Records", panel)
        self.assertIn('role="search"', panel)
        self.assertIn('name="search"', panel)
        self.assertIn('name="status"', panel)

    def test_records_do_not_require_horizontal_scrolling(self):
        for label in (
            "Date",
            "File",
            "Plant",
            "Department",
            "Document Number",
            "Status",
            "Review",
        ):
            self.assertIn(f'data-label="{label}"', self.template)

        self.assertIn(
            ".approval-records-table {\n  width: 100%;\n  min-width: 0;",
            self.styles,
        )
        self.assertIn("@container approval-records (max-width: 760px)", self.styles)
        self.assertIn("overflow-x: hidden", self.styles)


if __name__ == "__main__":
    unittest.main()
