import unittest
from unittest.mock import patch

from flask import Flask

from routes.document_library_routes import document_library_bp


class IatfCapaDownloadTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test"
        app.register_blueprint(document_library_bp)
        self.client = app.test_client()

    @patch("routes.document_library_routes.AuthService.is_logged_in", return_value=True)
    def test_download_returns_supplied_excel_workbook(self, _logged_in):
        response = self.client.get("/document-library/iatf-audit-nc-capa-format")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.mimetype,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment", response.headers["Content-Disposition"])
        self.assertIn("Audit NCs Tracking Report", response.headers["Content-Disposition"])
        self.assertTrue(response.data.startswith(b"PK"))
        response.close()


if __name__ == "__main__":
    unittest.main()
