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
            "send_quarterly_document_reminder",
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
        recipients, record, document_url, revision_url = send.call_args.args
        self.assertEqual(record["file_name"], "current.pdf")
        self.assertEqual(
            set(recipients),
            {"l1@example.com", "l2@example.com", "dept@example.com", "owner@example.com"},
        )
        self.assertTrue(document_url.endswith(f"/dashboard/view/{record['id']}"))
        self.assertTrue(revision_url.endswith(f"/upload?revision_of={record['id']}"))

    def test_email_contains_revision_action(self):
        app = Flask(__name__)
        app.config.update(MAIL_DEFAULT_SENDER="noreply@example.com", TESTING=True)
        mail.init_app(app)
        record = {
            "file_name": "stored.pdf",
            "original_file_name": "Control <Plan>.pdf",
            "document_number": "ZRAI-DOC-P1-2026-001",
            "revision_number": "Rev.01",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
        }

        with app.app_context(), patch("services.mail_service.mail.send") as send:
            ok, error = MailService.send_quarterly_document_reminder(
                ["l1@example.com", "l2@example.com"],
                record,
                "https://portal.example/dashboard/view/1",
                "https://portal.example/upload?revision_of=1",
            )

        self.assertTrue(ok)
        self.assertIsNone(error)
        message = send.call_args.args[0]
        self.assertIn("Quarterly document review required", message.subject)
        self.assertIn("Upload Revised Document", message.html)
        self.assertIn("revision_of=1", message.html)
        self.assertIn("Control &lt;Plan&gt;.pdf", message.html)


if __name__ == "__main__":
    unittest.main()
