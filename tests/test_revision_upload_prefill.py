import gc
import os
import tempfile
import unittest

from app import app
from config import Config
from database import configure_database, get_connection, init_db
from services.user_store_service import UserStoreService


class RevisionUploadPrefillTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        configure_database({
            "DATABASE_ENGINE": "sqlite",
            "SQLITE_DB_PATH": os.path.join(self.temp_dir.name, "test.db"),
        })
        init_db()
        UserStoreService._seed_users()
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO documents
                (name, user_id, uploader_email, plant, department, file_name,
                 original_file_name, uploaded_at, approval_status, document_number,
                 revision_number, category)
            VALUES ('Uploader', 'U100', 'uploader@example.com', 'P1 - Trichy Plant',
                    'Quality Assurance', 'control-plan.pdf', 'Control Plan.pdf',
                    '2026-08-01', 'Approved', 'ZRAI-DOC-P1-2026-001', 'Rev.01', 'qms')
            """
        )
        document_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO category_documents
                (category, sub_category, plant, department, file_name, uploaded_at,
                 approval_status, revision_number)
            VALUES ('qms', 'L1:quality_manuals', 'P1 - Trichy Plant',
                    'Quality Assurance', 'control-plan.pdf', '2026-08-01',
                    'Approved', 'Rev.01')
            """
        )
        connection.commit()
        connection.close()
        self.document = {
            "id": document_id,
            "document_number": "ZRAI-DOC-P1-2026-001",
        }

        self.client = app.test_client()
        admin = next(
            user for user in UserStoreService.get_all_users()
            if user.get("role") == "Admin"
        )
        with self.client.session_transaction() as session:
            session.update({
                "user_email": admin["email"],
                "user_name": admin["name"],
                "user_id": admin["user_id"],
                "user_role": "Admin",
                "user_qms_level": "L1",
            })

    def tearDown(self):
        configure_database({
            "DATABASE_ENGINE": Config.DATABASE_ENGINE,
            "SQLITE_DB_PATH": Config.SQLITE_DB_PATH,
        })
        gc.collect()
        self.temp_dir.cleanup()

    def test_approved_document_has_revision_button_and_prefilled_upload(self):
        document = self.document

        view_response = self.client.get(f"/dashboard/view/{document['id']}")
        self.assertEqual(view_response.status_code, 200)
        self.assertIn(b"Upload revised document", view_response.data)
        self.assertIn(
            f"/upload?revision_of={document['id']}".encode(),
            view_response.data,
        )
        view_response.close()

        upload_response = self.client.get(f"/upload?revision_of={document['id']}")
        self.assertEqual(upload_response.status_code, 200)
        self.assertIn(b"Upload Revised Document", upload_response.data)
        self.assertIn(document["document_number"].encode(), upload_response.data)
        self.assertIn(b"window.REVISION_PREFILL", upload_response.data)
        upload_response.close()


if __name__ == "__main__":
    unittest.main()
