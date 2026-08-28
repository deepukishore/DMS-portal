import unittest
from pathlib import Path
from unittest.mock import patch

from app import app
from services.auth_service import AuthService


class ApprovalQueueAccessTests(unittest.TestCase):
    def test_admin_l1_and_l2_can_access_queue(self):
        allowed_users = (
            {"role": "Admin", "qms_level": "L4"},
            {"role": "User", "qms_level": "L1"},
            {"role": "User", "qms_level": "L2"},
        )
        for user in allowed_users:
            with self.subTest(user=user):
                self.assertTrue(AuthService.can_access_approval_queue(user))

    def test_l3_and_l4_cannot_access_queue(self):
        for qms_level in ("L3", "L4"):
            with self.subTest(qms_level=qms_level):
                self.assertFalse(
                    AuthService.can_access_approval_queue(
                        {"role": "User", "qms_level": qms_level}
                    )
                )

    def test_unauthorized_user_is_redirected_from_queue_and_export(self):
        with app.test_client() as client, patch(
            "routes.approval_routes.AuthService.is_logged_in", return_value=True
        ), patch(
            "routes.approval_routes.AuthService.can_access_approval_queue",
            return_value=False,
        ):
            for path in ("/approvals", "/approvals/export"):
                with self.subTest(path=path):
                    response = client.get(path)
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(response.location.endswith("/dashboard"))

    def test_navigation_and_dashboard_links_are_permission_guarded(self):
        project_root = Path(__file__).resolve().parent.parent
        templates = project_root / "templates"
        for relative_path in (
            "components/sidebar.html",
            "components/sidebar_new.html",
        ):
            with self.subTest(template=relative_path):
                source = (templates / relative_path).read_text(encoding="utf-8")
                self.assertIn("{% if can_access_approval_queue %}", source)

        dashboard = (templates / "dashboard.html").read_text(encoding="utf-8")
        self.assertIn(
            "{% if endpoint != 'approvals.index' or can_access_approval_queue %}",
            dashboard,
        )


if __name__ == "__main__":
    unittest.main()
