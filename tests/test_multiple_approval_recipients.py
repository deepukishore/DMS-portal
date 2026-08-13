import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask

from routes.approval_routes import approval_bp
from routes.approval_routes import _normalize_selected_recipients


class MultipleApprovalRecipientTests(unittest.TestCase):
    def test_normalizes_deduplicates_and_preserves_multiple_emails(self):
        self.assertEqual(
            _normalize_selected_recipients(
                ["First@Example.com", "second@example.com", "first@example.com"]
            ),
            ["first@example.com", "second@example.com"],
        )

    def test_accepts_legacy_comma_and_semicolon_separated_values(self):
        self.assertEqual(
            _normalize_selected_recipients(
                ["first@example.com, second@example.com;third@example.com"]
            ),
            ["first@example.com", "second@example.com", "third@example.com"],
        )

    def test_review_form_uses_repeated_recipient_checkboxes(self):
        project_root = Path(__file__).resolve().parent.parent
        template = (project_root / "templates" / "approval_review.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('class="review-recipient-picker"', template)
        self.assertIn('type="checkbox"', template)
        self.assertIn('name="selected_recipients"', template)
        self.assertIn("Select one or more email recipients.", template)
        self.assertIn('id="recipient-search-input"', template)
        self.assertIn("Search by name, email, or department", template)
        self.assertIn('data-recipient-search="', template)
        self.assertIn("option.hidden = !matches", template)

    def test_first_approval_saves_all_selected_recipient_emails(self):
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY="test",
            APPROVAL_RECIPIENT="approver@example.com",
            FINAL_APPROVAL_RECIPIENT="final@example.com",
        )
        app.register_blueprint(approval_bp)
        client = app.test_client()
        record = {
            "id": 7,
            "approval_status": "Pending",
            "file_name": "document.pdf",
            "original_file_name": "document.pdf",
        }
        updated_record = {
            **record,
            "approval_status": "Pending Final Approval",
            "selected_recipients": "first@example.com,second@example.com",
        }

        with (
            patch("routes.approval_routes.AuthService.is_logged_in", return_value=True),
            patch(
                "routes.approval_routes.AuthService.get_current_user",
                return_value={"name": "First Approver", "email": "approver@example.com"},
            ),
            patch("routes.approval_routes._resolve_record_or_none", return_value=record),
            patch("routes.approval_routes._can_decide_record", return_value=True),
            patch(
                "routes.approval_routes.UserStoreService.get_all_users",
                return_value=[
                    {"email": "first@example.com"},
                    {"email": "second@example.com"},
                ],
            ),
            patch(
                "routes.approval_routes.DocumentService.update_approval_status",
                return_value=(updated_record, None),
            ) as update_status,
            patch("routes.approval_routes.SystemLogService.log_approval_decision"),
            patch("routes.approval_routes.SystemLogService.log_approval_email"),
            patch(
                "routes.approval_routes.MailService.send_document_approval_request",
                return_value=(True, None),
            ),
            patch("routes.approval_routes.NotificationService.notify_qms_level"),
        ):
            response = client.post(
                "/approvals/review/token/decision",
                data={
                    "status": "First Approved",
                    "selected_recipients": [
                        "FIRST@example.com",
                        "second@example.com",
                    ],
                },
                headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["ok"])
        self.assertEqual(
            update_status.call_args.kwargs["selected_recipients"],
            "first@example.com,second@example.com",
        )


if __name__ == "__main__":
    unittest.main()
