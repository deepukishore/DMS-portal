from datetime import datetime

from database import get_connection
from services.user_store_service import UserStoreService


class NotificationService:
    """Handles in-app notification delivery and read state."""

    @staticmethod
    def create_notification(user_email, title, message, link_url="", notification_type="info"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO notifications (user_email, title, message, link_url, notification_type, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            ''',
            (
                user_email,
                title,
                message,
                link_url,
                notification_type,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def notify_admins(title, message, link_url="", notification_type="info"):
        for admin in UserStoreService.get_admin_users():
            NotificationService.create_notification(
                admin["email"],
                title,
                message,
                link_url=link_url,
                notification_type=notification_type,
            )

    @staticmethod
    def notify_qms_level(qms_level, title, message, link_url="", notification_type="info"):
        for user in UserStoreService.get_users_by_qms_level(qms_level):
            NotificationService.create_notification(
                user["email"],
                title,
                message,
                link_url=link_url,
                notification_type=notification_type,
            )

    @staticmethod
    def get_recent_for_user(user_email, limit=8):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM notifications
            WHERE user_email = ?
            ORDER BY is_read ASC, created_at DESC, id DESC
            LIMIT ?
            ''',
            (user_email, limit),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        for row in rows:
            row["message"] = row.get("message", "").replace(
                "final HOD approval",
                "final approval",
            )
        return rows

    @staticmethod
    def get_unread_count(user_email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) AS count FROM notifications WHERE user_email = ? AND is_read = 0',
            (user_email,),
        )
        count = cursor.fetchone()["count"]
        conn.close()
        return count

    @staticmethod
    def mark_read(user_email, notification_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE notifications SET is_read = 1 WHERE id = ? AND user_email = ?',
            (int(notification_id), user_email),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def mark_all_read(user_email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE notifications SET is_read = 1 WHERE user_email = ? AND is_read = 0',
            (user_email,),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected

    @staticmethod
    def clear_all(user_email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM notifications WHERE user_email = ?',
            (user_email,),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected
