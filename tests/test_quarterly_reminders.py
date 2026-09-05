import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

from flask import Flask

from config import Config
from database import configure_database, get_connection, init_db
from extensions import mail
from services.mail_service import MailService
from services.quarterly_reminder_service import QuarterlyReminderService


class QuarterlyReminderTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        configure_database({"DATABASE_ENGINE": "sqlite", "SQLITE_DB_PATH": self.db_path})
        init_db()

        conn = get_connection()
        conn.executemany(
            """
            INSERT INTO users
                (email, name, user_id, role, password_hash, department, qms_level)
            VALUES (?, ?, ?, ?, 'hash', ?, ?)
            """,
            [
                ("l1@example.com", "L1 User", "U1", "User", "Finance", "L1"),
                ("l2@example.com", "L2 User", "U2", "User", "Quality", "L2"),
                ("dept@example.com", "Department User", "U3", "User", "Quality", "L4"),
                ("other@example.com", "Other User", "U4", "User", "HR", "L4"),
            ],
        )
        conn.executemany(
            """
            INSERT INTO documents
                (name, user_id, uploader_email, plant, department, file_name,
                 original_file_name, uploaded_at, approval_status, document_number,
                 revision_number, category)
            VALUES ('Uploader', 'U9', 'owner@example.com', 'P1 - Trichy Plant',
                    'Quality', ?, ?, '2026-08-01', ?, ?, ?, 'qms')
            """,
            [
                ("old.pdf", "old.pdf", "Approved", "ZRAI-DOC-P1-2026-001", "Rev.00"),
                ("current.pdf", "current.pdf", "Approved", "ZRAI-DOC-P1-2026-001", "Rev.01"),
                ("pending.pdf", "pending.pdf", "Pending", "ZRAI-DOC-P1-2026-002", "Rev.00"),
            ],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        configure_database(
            {"DATABASE_ENGINE": Config.DATABASE_ENGINE, "SQLITE_DB_PATH": Config.SQLITE_DB_PATH}
        )
        self.temp_dir.cleanup()

    def test_sends_latest_approved_document_only_once_per_quarter(self):
        with patch.object(
            MailService,
            "send_quarterly_document_digest",
            return_value=(True, None),
        ) as send:
            first = QuarterlyReminderService.send_due_reminders(
                "https://portal.example", now=datetime(2026, 7, 1, 9, 0)
            )
            second = QuarterlyReminderService.send_due_reminders(
                "https://portal.example", now=datetime(2026, 9, 30, 12, 0)
            )

        self.assertEqual(first["sent"], 1)
        self.assertEqual(second["sent"], 0)
        self.assertEqual(second["skipped"], 1)
        send.assert_called_once()
        recipient, recipient_name, records, base_url = send.call_args.args
        self.assertEqual(recipient, "l2@example.com")
        self.assertEqual(recipient_name, "L2 User")
        self.assertEqual([record["file_name"] for record in records], ["current.pdf"])
        self.assertEqual(base_url, "https://portal.example")
        self.assertEqual(first["documents"], 1)

    def test_manual_run_can_resend_reminders_in_the_same_quarter(self):
        with patch.object(
            MailService,
            "send_quarterly_document_digest",
            return_value=(True, None),
        ) as send:
            first = QuarterlyReminderService.send_due_reminders(
                "https://portal.example", now=datetime(2026, 7, 1, 9, 0)
            )
            manual = QuarterlyReminderService.send_due_reminders(
                "https://portal.example",
                now=datetime(2026, 8, 15, 11, 0),
                force=True,
            )

        self.assertEqual(first["sent"], 1)
        self.assertEqual(manual["sent"], 1)
        self.assertEqual(manual["skipped"], 0)
        self.assertEqual(send.call_count, 2)

    def test_documents_are_filtered_by_department_and_configured_category(self):
        documents = [
            {"id": 1, "department": "Quality", "category": "qms"},
            {"id": 2, "department": "Quality", "category": "csr"},
            {"id": 3, "department": "Finance", "category": "csr"},
        ]
        relevant = QuarterlyReminderService.documents_for_recipient(
            {
                "department": "QAD - Quality Assurance Department",
                "document_categories": "csr",
            },
            documents,
        )
        self.assertEqual([record["id"] for record in relevant], [2])

    def test_digest_email_contains_all_relevant_documents_and_revision_actions(self):
        app = Flask(__name__)
        app.config.update(MAIL_DEFAULT_SENDER="noreply@example.com", TESTING=True)
        mail.init_app(app)
        records = [
            {
                "id": 1,
                "file_name": "stored.pdf",
                "original_file_name": "Control <Plan>.pdf",
                "document_number": "ZRAI-DOC-P1-2026-001",
                "revision_number": "Rev.01",
                "plant": "P1 - Trichy Plant",
                "department": "Quality",
                "category": "qms",
            },
            {
                "id": 2,
                "file_name": "audit-report.pdf",
                "document_number": "ZRAI-DOC-P1-2026-002",
                "revision_number": "Rev.00",
                "plant": "P1 - Trichy Plant",
                "department": "Quality",
                "category": "audit_reports",
            },
        ]

        with app.app_context(), patch("services.mail_service.mail.send") as send:
            ok, error = MailService.send_quarterly_document_digest(
                "l2@example.com",
                "L2 Reviewer",
                records,
                "https://portal.example",
            )

        self.assertTrue(ok)
        self.assertIsNone(error)
        message = send.call_args.args[0]
        self.assertEqual(message.recipients, ["l2@example.com"])
        self.assertIn("2 relevant document(s)", message.subject)
        self.assertIn("Control &lt;Plan&gt;.pdf", message.html)
        self.assertIn("audit-report.pdf", message.html)
        self.assertIn("revision_of=1", message.html)
        self.assertIn("revision_of=2", message.html)
        self.assertEqual(message.html.count("Upload revised document"), 2)


if __name__ == "__main__":
    unittest.main()
