import unittest
from unittest.mock import patch

from app import app
from services.mail_service import MailService


class ApprovalRequestEmailTests(unittest.TestCase):
    def test_approval_request_uses_branded_action_email(self):
        record = {
            "file_name": "stored-file.pdf",
            "original_file_name": "Control Plan <Draft>.pdf",
            "name": "Dinesh Kumar",
            "user_id": "EMP014",
            "plant": "P2 - Guduvanchery Plant",
            "department": "Quality",
            "customer": "ZF",
            "document_number": "ZRAI-DOC-P2-2026-014",
            "revision_number": "Rev.02",
            "category": "QMS",
            "uploaded_at": "2026-08-14 10:30:00",
            "approval_status": "Pending",
        }

        with app.app_context(), patch("services.mail_service.mail.send") as send:
            ok, error = MailService.send_document_approval_request(
                ["approver@example.com"],
                "https://portal.example/approvals/review/token",
                record,
            )

        self.assertTrue(ok)
        self.assertIsNone(error)
        message = send.call_args.args[0]
        self.assertIn("Action required - First-stage approval", message.subject)
        self.assertIn("Document Approval Request", message.html)
        self.assertIn("Approval Status:</strong> Pending first-stage review", message.html)
        self.assertIn("Review Document", message.html)
        self.assertIn("Rane Group | Confidential Information", message.html)
        self.assertIn("Control Plan &lt;Draft&gt;.pdf", message.html)
        self.assertNotIn("Control Plan <Draft>.pdf", message.html)

    def test_final_stage_email_identifies_final_approval(self):
        record = {
            "file_name": "final-review.pdf",
            "name": "Uploader",
            "user_id": "EMP001",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "ZF",
            "approval_status": "Pending Final Approval",
        }

        with app.app_context(), patch("services.mail_service.mail.send") as send:
            ok, error = MailService.send_document_approval_request(
                "final@example.com",
                "https://portal.example/approvals/review/final-token",
                record,
            )

        self.assertTrue(ok)
        self.assertIsNone(error)
        message = send.call_args.args[0]
        self.assertIn("Action required - Final approval", message.subject)
        self.assertIn("Pending final approval", message.html)

    def test_decision_email_header_color_matches_response(self):
        record = {
            "file_name": "control-plan.pdf",
            "name": "Uploader",
            "user_id": "EMP001",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "ZF",
            "document_number": "ZRAI-DOC-P1-2026-001",
            "revision_number": "Rev.01",
            "category": "QMS",
        }
        expected = {
            "Approved": ("#168a50", "Document Approved"),
            "Hold": ("#c77800", "Document Update Required"),
            "Rejected": ("#b42318", "Document Rejected"),
        }

        for status, (header_color, title) in expected.items():
            with self.subTest(status=status), app.app_context(), patch(
                "services.mail_service.mail.send"
            ) as send:
                ok, error = MailService.send_approval_decision_notification(
                    "uploader@example.com",
                    record,
                    status,
                    "2026-08-14 15:55:24",
                    rejection_comment="Please update the document." if status != "Approved" else "",
                )

            self.assertTrue(ok)
            self.assertIsNone(error)
            message = send.call_args.args[0]
            self.assertIn(title, message.html)
            self.assertIn(f"background:{header_color}", message.html)

    def test_approved_shared_email_uses_green_header(self):
        record = {
            "file_name": "approved-document.pdf",
            "name": "Uploader",
            "user_id": "EMP001",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "document_number": "ZRAI-DOC-P1-2026-001",
            "revision_number": "Rev.01",
            "first_approver": "First Reviewer",
            "final_approver": "Final Reviewer",
        }

        with app.app_context(), patch("services.mail_service.mail.send") as send:
            ok, error = MailService.send_final_shared_notification(
                ["recipient@example.com"], record, "2026-08-14 15:55:24"
            )

        self.assertTrue(ok)
        self.assertIsNone(error)
        message = send.call_args.args[0]
        self.assertIn("Document Approved and Shared", message.html)
        self.assertIn("background:#168a50", message.html)
        self.assertIn("Status:</strong>", message.html)


if __name__ == "__main__":
    unittest.main()
