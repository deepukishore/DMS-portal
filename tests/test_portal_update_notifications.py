import os
import tempfile
import unittest
from unittest.mock import patch

from flask import Flask

from config import Config
from database import configure_database, get_connection, init_db
from extensions import mail
from routes.notification_routes import notification_bp
from services.mail_service import MailService
from services.notification_service import NotificationService


class PortalUpdateNotificationServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        configure_database({"DATABASE_ENGINE": "sqlite", "SQLITE_DB_PATH": self.db_path})
        init_db()
        connection = get_connection()
        try:
            connection.executemany(
                """
                INSERT INTO users
                    (email, name, user_id, role, password_hash, qms_level)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    ("admin@example.com", "Admin", "U001", "Admin", "unused", "L1"),
                    ("user@example.com", "User", "U002", "User", "unused", "L4"),
                ],
            )
            connection.commit()
        finally:
            connection.close()

    def tearDown(self):
        configure_database(
            {"DATABASE_ENGINE": Config.DATABASE_ENGINE, "SQLITE_DB_PATH": Config.SQLITE_DB_PATH}
        )
        self.temp_dir.cleanup()

    def test_portal_update_reaches_every_user_and_popup_is_one_time(self):
        delivered = NotificationService.notify_all_users(
            "New search",
            "The portal now has an improved document search.",
            link_url="/document-library",
        )

        self.assertEqual(delivered, 2)
        popup = NotificationService.get_unseen_portal_update("user@example.com")
        self.assertEqual(popup["title"], "New search")
        self.assertEqual(popup["notification_type"], "portal_update")
        self.assertEqual(NotificationService.get_unread_count("user@example.com"), 1)

        self.assertTrue(
            NotificationService.mark_popup_seen("user@example.com", popup["id"])
        )
        self.assertIsNone(
            NotificationService.get_unseen_portal_update("user@example.com")
        )
        self.assertEqual(
            NotificationService.get_unread_count("user@example.com"),
            1,
            "Dismissing the popup must keep the notification unread in the bell menu.",
        )


class PortalUpdateNotificationRouteTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test"
        app.register_blueprint(notification_bp)
        self.client = app.test_client()

    @patch("routes.notification_routes.AuthService.is_admin", return_value=False)
    @patch("routes.notification_routes.AuthService.is_logged_in", return_value=True)
    def test_non_admin_cannot_publish_portal_update(self, _logged_in, _is_admin):
        response = self.client.post(
            "/notifications/portal-updates",
            data={"title": "Update", "message": "Details", "link_url": ""},
        )
        self.assertEqual(response.status_code, 403)

    @patch("routes.notification_routes.AuthService.is_admin", return_value=False)
    @patch("routes.notification_routes.AuthService.is_logged_in", return_value=True)
    def test_non_admin_cannot_send_quarterly_reminders(self, _logged_in, _is_admin):
        response = self.client.post("/notifications/quarterly-reminders/send")
        self.assertEqual(response.status_code, 403)

    @patch("routes.notification_routes.SystemLogService.log_manual_quarterly_reminders")
    @patch(
        "routes.notification_routes.QuarterlyReminderService.send_due_reminders",
        return_value={
            "quarter": "2026-Q3",
            "sent": 4,
            "failed": 0,
            "skipped": 0,
            "documents": 12,
        },
    )
    @patch("routes.notification_routes.AuthService.is_admin", return_value=True)
    @patch("routes.notification_routes.AuthService.is_logged_in", return_value=True)
    def test_admin_can_send_quarterly_reminders_manually(
        self,
        _logged_in,
        _is_admin,
        send_reminders,
        log_manual_run,
    ):
        with self.client.session_transaction() as session:
            session["user_email"] = "admin@example.com"
            session["user_name"] = "Administrator"

        response = self.client.post("/notifications/quarterly-reminders/send")

        self.assertEqual(response.status_code, 302)
        send_reminders.assert_called_once_with("http://localhost", force=True)
        log_manual_run.assert_called_once_with(
            "admin@example.com",
            "Administrator",
            {
                "quarter": "2026-Q3",
                "sent": 4,
                "failed": 0,
                "skipped": 0,
                "documents": 12,
            },
        )

    @patch("routes.notification_routes.SystemLogService.log_portal_update")
    @patch("routes.notification_routes.MailService.send_portal_update", return_value=(True, None))
    @patch(
        "routes.notification_routes.UserStoreService.get_all_users",
        return_value=[
            {"email": "admin@example.com"},
            {"email": "user@example.com"},
        ],
    )
    @patch("routes.notification_routes.NotificationService.notify_all_users", return_value=12)
    @patch("routes.notification_routes.AuthService.is_admin", return_value=True)
    @patch("routes.notification_routes.AuthService.is_logged_in", return_value=True)
    def test_admin_can_publish_update_to_all_users(
        self,
        _logged_in,
        _is_admin,
        notify_all,
        get_users,
        send_email,
        log_update,
    ):
        with self.client.session_transaction() as session:
            session["user_email"] = "admin@example.com"
            session["user_name"] = "Administrator"

        response = self.client.post(
            "/notifications/portal-updates",
            data={
                "title": "New portal feature",
                "message": "A new portal feature is now available.",
                "link_url": "/dashboard",
            },
        )

        self.assertEqual(response.status_code, 302)
        notify_all.assert_called_once_with(
            "New portal feature",
            "A new portal feature is now available.",
            link_url="/dashboard",
            notification_type="portal_update",
        )
        get_users.assert_called_once_with()
        send_email.assert_called_once_with(
            ["admin@example.com", "user@example.com"],
            "New portal feature",
            "A new portal feature is now available.",
            "http://localhost/dashboard",
        )
        log_update.assert_called_once_with(
            "admin@example.com",
            "Administrator",
            "New portal feature",
            12,
        )

    def test_portal_update_email_is_branded_and_uses_bcc(self):
        app = Flask(__name__)
        app.config.update(MAIL_DEFAULT_SENDER="noreply@example.com", TESTING=True)
        mail.init_app(app)

        with app.app_context(), patch("services.mail_service.mail.send") as send:
            ok, error = MailService.send_portal_update(
                ["USER@example.com", "user@example.com", "admin@example.com"],
                "Search <improved>",
                "The portal now includes faster document search.",
                "https://portal.example/dashboard",
            )

        self.assertTrue(ok)
        self.assertIsNone(error)
        email = send.call_args.args[0]
        self.assertEqual(email.recipients, [])
        self.assertEqual(email.bcc, ["admin@example.com", "user@example.com"])
        self.assertIn("Portal Update", email.html)
        self.assertIn("Search &lt;improved&gt;", email.html)
        self.assertIn("Open Portal", email.html)
        self.assertIn("https://portal.example/dashboard", email.html)


if __name__ == "__main__":
    unittest.main()
