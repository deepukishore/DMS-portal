import os
import tempfile
import unittest
from io import BytesIO

from werkzeug.datastructures import FileStorage

from config import Config
from database import configure_database, get_connection, init_db
from services.document_service import DocumentService


def _pdf(name):
    return FileStorage(
        stream=BytesIO(b"%PDF-1.4\n%%EOF"),
        filename=name,
        content_type="application/pdf",
    )


class DocumentNumberingTests(unittest.TestCase):
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

    def _save(self, plant, name):
        record, error = DocumentService.save_upload(
            _pdf(name),
            "Uploader",
            "U100",
            "uploader@example.com",
            plant,
            "Quality",
            "Internal",
            self.upload_dir,
            "",
            "Rev.00",
            "qms",
        )
        self.assertIsNone(error)
        return record

    def test_automatic_numbers_are_sequential_per_plant(self):
        first_p1 = self._save("P1 - Trichy Plant", "first.pdf")
        second_p1 = self._save("P1 - Trichy Plant", "second.pdf")
        first_p2 = self._save("P2 - Guduvanchery Plant", "third.pdf")

        self.assertEqual(first_p1["document_number"], "ZRAI-DOC-P1-2026-001")
        self.assertEqual(second_p1["document_number"], "ZRAI-DOC-P1-2026-002")
        self.assertEqual(first_p2["document_number"], "ZRAI-DOC-P2-2026-001")
        self.assertEqual(
            DocumentService.peek_next_document_number("P1"),
            "ZRAI-DOC-P1-2026-003",
        )

    def test_existing_numbers_are_not_reused(self):
        conn = get_connection()
        conn.execute(
            """INSERT INTO documents
               (name, user_id, uploader_email, plant, department, customer, file_name,
                uploaded_at, document_number)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "Legacy",
                "U1",
                "legacy@example.com",
                "P3 - Guduvanchery Plant",
                "Quality",
                "Internal",
                "legacy.pdf",
                "2026-01-01",
                "ZRAI-DOC-P3-2026-007",
            ),
        )
        conn.commit()
        conn.close()

        existing = DocumentService.get_document_by_document_number(
            "ZRAI-DOC-P3-2026-007"
        )
        self.assertIsNotNone(existing)
        self.assertEqual(existing["original_file_name"], None)

        record = self._save("P3 - Guduvanchery Plant", "next.pdf")
        self.assertEqual(record["document_number"], "ZRAI-DOC-P3-2026-008")

    def test_unknown_revision_document_number_is_not_found(self):
        self.assertIsNone(
            DocumentService.get_document_by_document_number(
                "ZRAI-DOC-P1-2026-999"
            )
        )

    def test_revision_document_number_is_validated(self):
        self.assertEqual(
            DocumentService.validate_document_number(
                "ZRAI-DOC-P4-2026-009",
                plant="P4 - Uttarakhand Plant",
            ),
            "ZRAI-DOC-P4-2026-009",
        )
        with self.assertRaises(ValueError):
            DocumentService.validate_document_number(
                "009",
                plant="P4 - Uttarakhand Plant",
            )
        with self.assertRaises(ValueError):
            DocumentService.validate_document_number(
                "ZRAI-DOC-P3-2026-009",
                plant="P4 - Uttarakhand Plant",
            )


if __name__ == "__main__":
    unittest.main()
