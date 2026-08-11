import os
import tempfile
import unittest
from io import BytesIO

from werkzeug.datastructures import FileStorage

from config import Config
from database import configure_database, get_connection, init_db
from services.document_service import DocumentService


def _pdf(name, content=b"%PDF-1.4\n%%EOF"):
    return FileStorage(stream=BytesIO(content), filename=name, content_type="application/pdf")


class HoldResubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.upload_dir = os.path.join(self.temp_dir.name, "uploads")
        os.makedirs(self.upload_dir)
        configure_database({"DATABASE_ENGINE": "sqlite", "SQLITE_DB_PATH": self.db_path})
        init_db()

    def tearDown(self):
        configure_database(
            {"DATABASE_ENGINE": Config.DATABASE_ENGINE, "SQLITE_DB_PATH": Config.SQLITE_DB_PATH}
        )
        self.temp_dir.cleanup()

    def _new_document(self):
        record, error = DocumentService.save_upload(
            _pdf("procedure.pdf"),
            "Original Uploader",
            "U100",
            "uploader@example.com",
            "P1 - Trichy Plant",
            "Quality",
            "Internal",
            self.upload_dir,
            "DOC-100",
            "Rev.01",
            "qms",
        )
        self.assertIsNone(error)
        return record

    def test_first_stage_hold_returns_to_first_reviewer_after_uploader_resubmits(self):
        record = self._new_document()
        not_held, error = DocumentService.update_approval_status(
            record["id"], "Hold", "", decided_by="First Reviewer"
        )
        self.assertIsNone(not_held)
        self.assertIn("corrections needed", error)

        held, error = DocumentService.update_approval_status(
            record["id"], "Hold", "Correct section 4.", decided_by="First Reviewer"
        )
        self.assertIsNone(error)
        self.assertEqual(held["hold_comment"], "Correct section 4.")

        denied, error = DocumentService.resubmit_held_document(
            record["id"],
            _pdf("wrong-user.pdf"),
            "Someone Else",
            "U200",
            "other@example.com",
            self.upload_dir,
            "Updated section 4.",
        )
        self.assertIsNone(denied)
        self.assertIn("original uploader", error)

        updated, error = DocumentService.resubmit_held_document(
            record["id"],
            _pdf("procedure-corrected.pdf"),
            "Original Uploader",
            "U100",
            "uploader@example.com",
            self.upload_dir,
            "Updated section 4 and corrected the owner.",
            revision_number="Rev.02",
        )
        self.assertIsNone(error)
        self.assertEqual(updated["approval_status"], "Pending")
        self.assertEqual(updated["current_version"], 2)
        self.assertEqual(updated["resubmission_comment"], "Updated section 4 and corrected the owner.")
        self.assertEqual(updated["hold_comment"], "Correct section 4.")
        self.assertEqual(len(DocumentService.get_versions(record["id"])), 2)

    def test_final_stage_hold_returns_to_final_reviewer(self):
        record = self._new_document()
        DocumentService.update_approval_status(
            record["id"],
            "First Approved",
            decided_by="First Reviewer",
            selected_recipients="owner@example.com",
        )
        DocumentService.update_approval_status(
            record["id"], "Hold", "Update the effective date.", decided_by="Final Reviewer"
        )

        updated, error = DocumentService.resubmit_held_document(
            record["id"],
            _pdf("procedure-final-correction.pdf"),
            "Original Uploader",
            "U100",
            "uploader@example.com",
            self.upload_dir,
            "Effective date updated.",
        )
        self.assertIsNone(error)
        self.assertEqual(updated["approval_status"], "Pending Final Approval")
        self.assertEqual(updated["first_approver"], "First Reviewer")
        self.assertTrue(updated["first_approved_at"])


if __name__ == "__main__":
    unittest.main()
