from datetime import datetime

from database import get_connection


class SystemLogService:
    """Handles audit logging for user and approval actions."""

    @staticmethod
    def _entry(user_email, user_name, action_type, details, ip_address="-"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO system_logs (timestamp, user_name, user_id, action, details)
                         VALUES (?, ?, ?, ?, ?)''',
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_name, user_email, action_type, details)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def log_login(user_email, user_name, ip_address="-"):
        SystemLogService._entry(user_email, user_name, "LOGIN", "User logged in.", ip_address)

    @staticmethod
    def log_logout(user_email, user_name):
        SystemLogService._entry(user_email, user_name, "LOGOUT", "User logged out.")

    @staticmethod
    def log_register(user_email, user_name, ip_address="-"):
        SystemLogService._entry(user_email, user_name, "REGISTER", "New account created.", ip_address)

    @staticmethod
    def log_upload(user_email, user_name, file_name, plant, department):
        SystemLogService._entry(
            user_email,
            user_name,
            "UPLOAD",
            f'Uploaded "{file_name}" to {plant} / {department}.',
        )

    @staticmethod
    def log_delete(user_email, user_name, file_name, plant, department):
        SystemLogService._entry(
            user_email,
            user_name,
            "DELETE",
            f'Deleted "{file_name}" from {plant} / {department}.',
        )

    @staticmethod
    def log_view(user_email, user_name, file_name, context):
        SystemLogService._entry(
            user_email,
            user_name,
            "VIEW",
            f'Viewed "{file_name}" in {context}.',
        )

    @staticmethod
    def log_approval_email(recipient_email, file_name):
        SystemLogService._entry(
            recipient_email,
            "Approval Request",
            "APPROVAL_EMAIL",
            f'Sent approval email for "{file_name}".',
        )

    @staticmethod
    def log_approval_decision(approver_email, file_name, status, approver_name="Approver"):
        action = "APPROVED" if status == "Approved" else "REJECTED"
        SystemLogService._entry(
            approver_email,
            approver_name,
            action,
            f'{status} "{file_name}".',
        )

    @staticmethod
    def get_all_logs():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM system_logs ORDER BY timestamp DESC')
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        # Map 'action' to 'action_type' for compatibility
        for log in logs:
            log['action_type'] = log.get('action', '')
            log['user_email'] = log.get('user_id', '')
        return logs

    @staticmethod
    def get_logs_by_action(action_type):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM system_logs WHERE action = ? ORDER BY timestamp DESC', (action_type,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        for log in logs:
            log['action_type'] = log.get('action', '')
            log['user_email'] = log.get('user_id', '')
        return logs

    @staticmethod
    def get_logs_by_user(user_email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM system_logs WHERE user_id = ? ORDER BY timestamp DESC', (user_email,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        for log in logs:
            log['action_type'] = log.get('action', '')
            log['user_email'] = log.get('user_id', '')
        return logs

    @staticmethod
    def log_password_change(user_email, user_name):
        SystemLogService._entry(user_email, user_name, "PASSWORD_CHANGE", "Password updated successfully.")
