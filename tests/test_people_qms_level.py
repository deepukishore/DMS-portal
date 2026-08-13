import os
import tempfile
import unittest
from unittest.mock import patch

from flask import Flask, session

from config import Config
from database import configure_database, get_connection, init_db
from routes.people_routes import people_bp
from services.auth_service import AuthService
from services.user_store_service import UserStoreService


class QmsLevelStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        configure_database({"DATABASE_ENGINE": "sqlite", "SQLITE_DB_PATH": self.db_path})
        init_db()
        connection = get_connection()
        try:
            connection.execute(
                """INSERT INTO users
                   (email, name, user_id, plant, department, role, password_hash, qms_level)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "user@example.com",
                    "Standard User",
                    "U100",
                    "P1 - Trichy Plant",
                    "Quality",
                    "User",
                    "unused",
                    "L4",
                ),
            )
            connection.execute(
                """INSERT INTO users
                   (email, name, user_id, plant, department, role, password_hash, qms_level)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "admin@example.com",
                    "Administrator",
                    "U101",
                    "P1 - Trichy Plant",
                    "Quality",
                    "Admin",
                    "unused",
                    "L1",
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def tearDown(self):
        configure_database(
            {"DATABASE_ENGINE": Config.DATABASE_ENGINE, "SQLITE_DB_PATH": Config.SQLITE_DB_PATH}
        )
        self.temp_dir.cleanup()

    def test_updates_regular_user_qms_level(self):
        updated = UserStoreService.update_qms_level("user@example.com", "l2")
        self.assertEqual(updated["qms_level"], "L2")

    def test_admin_account_remains_l1(self):
        with self.assertRaisesRegex(ValueError, "always assigned"):
            UserStoreService.update_qms_level("admin@example.com", "L3")

    def test_rejects_unknown_level(self):
        with self.assertRaisesRegex(ValueError, "L1, L2, L3, or L4"):
            UserStoreService.update_qms_level("user@example.com", "L5")


class QmsLevelRouteTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test"
        app.register_blueprint(people_bp)
        self.client = app.test_client()

    @patch("routes.people_routes.AuthService.is_admin", return_value=False)
    @patch("routes.people_routes.AuthService.is_logged_in", return_value=True)
    def test_non_admin_cannot_update_level(self, _logged_in, _is_admin):
        response = self.client.post(
            "/people/qms-level",
            json={"email": "user@example.com", "qms_level": "L2"},
        )
        self.assertEqual(response.status_code, 403)

    @patch("routes.people_routes.SystemLogService.log_qms_level_change")
    @patch("routes.people_routes.UserStoreService.update_qms_level")
    @patch("routes.people_routes.UserStoreService.get_user_by_email")
    @patch("routes.people_routes.AuthService.is_admin", return_value=True)
    @patch("routes.people_routes.AuthService.is_logged_in", return_value=True)
    def test_admin_can_update_level(
        self,
        _logged_in,
        _is_admin,
        get_user,
        update_level,
        log_change,
    ):
        get_user.return_value = {
            "email": "user@example.com",
            "name": "Standard User",
            "role": "User",
            "qms_level": "L4",
        }
        update_level.return_value = {
            "email": "user@example.com",
            "name": "Standard User",
            "role": "User",
            "qms_level": "L2",
        }
        with self.client.session_transaction() as session:
            session["user_email"] = "admin@example.com"
            session["user_name"] = "Administrator"

        response = self.client.post(
            "/people/qms-level",
            json={"email": "user@example.com", "qms_level": "L2"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["user"]["qms_level"], "L2")
        update_level.assert_called_once_with("user@example.com", "L2")
        log_change.assert_called_once()

    def test_current_qms_level_refreshes_from_user_record(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test"
        with app.test_request_context("/"):
            session["user_qms_level"] = "L4"
            with patch.object(
                AuthService,
                "get_current_user",
                return_value={"role": "User", "qms_level": "L2"},
            ):
                self.assertEqual(AuthService.get_qms_level(), "L2")
                self.assertEqual(session["user_qms_level"], "L2")


if __name__ == "__main__":
    unittest.main()
