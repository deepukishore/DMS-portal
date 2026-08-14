from pathlib import Path
import unittest

from services.document_service import DocumentService


class DashboardReportRequestedUpdatesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parents[1]

    def read_template(self, name):
        return (self.project_root / "templates" / name).read_text(encoding="utf-8")

    def test_dashboard_replaces_daily_trend_with_bookmarks_table(self):
        template = self.read_template("dashboard.html")

        self.assertNotIn("dashboard-trend-chart", template)
        self.assertNotIn("daily_trend", template)
        self.assertIn("dashboard-bookmarks-table", template)
        self.assertIn("data-bookmark-row", template)

    def test_dashboard_search_and_documents_share_one_panel(self):
        template = self.read_template("dashboard.html")

        self.assertIn(
            'class="surface-panel dashboard-search-panel dashboard-documents-panel" id="documents"',
            template,
        )
        self.assertNotIn('id="dashboard-search"', template)
        self.assertEqual(template.count('<h2 class="section-title">Documents</h2>'), 1)

    def test_report_status_cards_link_to_filtered_documents(self):
        template = self.read_template("graphics_report.html")

        for status in ("Approved", "Pending", "Rejected", "Hold"):
            self.assertIn(f"status='{status}'", template)
        self.assertIn("url_for('dashboard.index', _anchor='documents')", template)

        for removed_heading in ("Plants", "Customers", "Departments", "Approval Rate"):
            self.assertNotIn(f"<h3>{removed_heading}</h3>", template)

    def test_pending_and_hold_filters_return_distinct_content(self):
        records = [
            {"id": 1, "approval_status": "Pending"},
            {"id": 2, "approval_status": "Pending Final Approval"},
            {"id": 3, "approval_status": "Hold"},
        ]

        pending = DocumentService.filter_by_status(records, "Pending")
        hold = DocumentService.filter_by_status(records, "Hold")
        self.assertEqual([record["id"] for record in pending], [1, 2])
        self.assertEqual([record["id"] for record in hold], [3])

    def test_report_registers_3d_depth_renderer(self):
        template = self.read_template("graphics_report.html")

        self.assertIn("const chart3DDepthPlugin", template)
        self.assertIn("Chart.register(chart3DDepthPlugin)", template)
        self.assertIn("meta.type === 'bar'", template)
        self.assertIn("meta.type === 'doughnut'", template)
        self.assertIn("if (visibleLength < 1) return", template)
        self.assertIn("function shadeChartColor", template)
        self.assertIn("const sideColor = shadeChartColor(frontColor, -.3)", template)

    def test_request_corrections_precedes_reject(self):
        template = self.read_template("approval_review.html")

        corrections_index = template.index('value="Hold" class="btn-decision btn-hold')
        reject_index = template.index('value="Rejected" class="btn-decision btn-reject')
        self.assertLess(corrections_index, reject_index)


if __name__ == "__main__":
    unittest.main()
