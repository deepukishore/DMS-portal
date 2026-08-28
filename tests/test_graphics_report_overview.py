import unittest
from pathlib import Path
from unittest.mock import patch

from app import app
from routes.graphics_report_routes import _get_statistics


class GraphicsReportOverviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project_root = Path(__file__).resolve().parents[1]
        cls.template = (project_root / "templates" / "graphics_report.html").read_text(
            encoding="utf-8"
        )
        cls.styles = (project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )

    def test_page_name_is_preserved(self):
        self.assertIn("{% block title %}Graphics Report", self.template)
        self.assertIn('<h1 class="page-title">Graphics Report</h1>', self.template)
        self.assertNotIn("Document Analytics", self.template)

    def test_dashboard_overview_and_scope_filters_are_present(self):
        for marker in (
            "report-scope-filter",
            "report-plant-tabs",
            "report-department",
            "report-kpi-grid",
            "report-total-card",
            "report-rate-card",
            "report-status-grid",
            "approvalRateTrendChart",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.template)
        self.assertIn(".report-kpi-grid", self.styles)
        self.assertIn(".report-status-card", self.styles)

    def test_approval_rate_uses_real_status_totals(self):
        stats = _get_statistics(
            [
                {"approval_status": "Approved", "uploaded_at": "2026-01-01"},
                {"approval_status": "Approved", "uploaded_at": "2026-01-02"},
                {"approval_status": "Pending", "uploaded_at": "2026-01-03"},
                {"approval_status": "Rejected", "uploaded_at": "2026-01-04"},
            ]
        )
        self.assertEqual(stats["overall"]["approval_rate"], 50.0)
        self.assertEqual(len(stats["approval_trend"]), 8)

    def test_report_route_renders_with_the_new_overview(self):
        records = [
            {
                "approval_status": "Approved",
                "uploaded_at": "2026-08-28 10:00:00",
                "plant": "P2 - Guduvanchery Plant",
                "department": "QAD - Quality Assurance Department",
                "category": "QMS",
            }
        ]
        with app.test_client() as client, patch(
            "routes.graphics_report_routes.AuthService.is_logged_in",
            return_value=True,
        ), patch(
            "routes.graphics_report_routes._get_records",
            return_value=records,
        ):
            response = client.get(
                "/graphics-report?plant=P2+-+Guduvanchery+Plant"
                "&department=QAD+-+Quality+Assurance+Department"
            )

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Graphics Report", html)
        self.assertIn("Total documents tracked", html)
        self.assertIn('value="QAD - Quality Assurance Department" selected', html)


if __name__ == "__main__":
    unittest.main()
