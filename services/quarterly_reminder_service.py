import json
import threading
from datetime import datetime

from data.departments import normalize_department
from database import get_connection
from services.document_service import DocumentService
from services.mail_service import MailService
from services.system_log_service import SystemLogService
from services.user_store_service import UserStoreService


class QuarterlyReminderService:
    """Send one update-review reminder per current approved document each quarter."""

    @staticmethod
    def quarter_key(now=None):
        now = now or datetime.now()
        return f"{now.year}-Q{((now.month - 1) // 3) + 1}"

    @staticmethod
    def current_approved_documents():
        latest = {}
        for record in DocumentService.get_all_documents():
            if record.get("approval_status") != "Approved":
                continue
            key = (record.get("document_number") or "").strip().upper()
            key = key or f"document:{record.get('id')}"
            if key not in latest or int(record.get("id") or 0) > int(latest[key].get("id") or 0):
                latest[key] = record
        return sorted(latest.values(), key=lambda item: int(item.get("id") or 0))

    @staticmethod
    def recipient_emails(record):
        """Include all L1/L2 users plus the uploader and same-department stakeholders."""
        recipients = set()
        document_department = normalize_department(record.get("department") or "").casefold()
        for user in UserStoreService.get_all_users():
            email = str(user.get("email") or "").strip().lower()
            if not email:
                continue
            qms_level = str(user.get("qms_level") or "").strip().upper()
            same_department = (
                document_department
                and normalize_department(user.get("department") or "").casefold() == document_department
            )
            if qms_level in {"L1", "L2"} or user.get("role") == "Admin" or same_department:
                recipients.add(email)

        uploader_email = str(record.get("uploader_email") or "").strip().lower()
        if uploader_email:
            recipients.add(uploader_email)
        return sorted(recipients)

    @staticmethod
    def _claim(quarter_key, document_id, attempted_at):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT status FROM quarterly_document_reminders WHERE quarter_key = ? AND document_id = ?",
                (quarter_key, int(document_id)),
            )
            existing = cursor.fetchone()
            if existing and existing["status"] in {"sending", "sent"}:
                return False
            if existing:
                cursor.execute(
                    """
                    UPDATE quarterly_document_reminders
                    SET status = 'sending', attempted_at = ?, sent_at = NULL, error = NULL
                    WHERE quarter_key = ? AND document_id = ? AND status = 'failed'
                    """,
                    (attempted_at, quarter_key, int(document_id)),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO quarterly_document_reminders
                        (quarter_key, document_id, status, attempted_at)
                    VALUES (?, ?, 'sending', ?)
                    """,
                    (quarter_key, int(document_id), attempted_at),
                )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _finish(quarter_key, document_id, recipients, error=None):
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE quarterly_document_reminders
            SET status = ?, sent_at = ?, recipients = ?, error = ?
            WHERE quarter_key = ? AND document_id = ?
            """,
            (
                "failed" if error else "sent",
                None if error else now_text,
                json.dumps(recipients),
                error,
                quarter_key,
                int(document_id),
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def send_due_reminders(base_url, now=None):
        now = now or datetime.now()
        quarter_key = QuarterlyReminderService.quarter_key(now)
        base_url = str(base_url or "").rstrip("/")
        result = {"quarter": quarter_key, "sent": 0, "failed": 0, "skipped": 0}

        for record in QuarterlyReminderService.current_approved_documents():
            document_id = int(record["id"])
            attempted_at = now.strftime("%Y-%m-%d %H:%M:%S")
            if not QuarterlyReminderService._claim(quarter_key, document_id, attempted_at):
                result["skipped"] += 1
                continue

            recipients = QuarterlyReminderService.recipient_emails(record)
            document_url = f"{base_url}/dashboard/view/{document_id}"
            revision_url = f"{base_url}/upload?revision_of={document_id}"
            sent, error = MailService.send_quarterly_document_reminder(
                recipients,
                record,
                document_url,
                revision_url,
            )
            QuarterlyReminderService._finish(
                quarter_key,
                document_id,
                recipients,
                error=None if sent else (error or "Email delivery failed."),
            )
            if sent:
                result["sent"] += 1
                SystemLogService.log_quarterly_reminder(
                    quarter_key,
                    record.get("file_name", "Document"),
                    len(recipients),
                )
            else:
                result["failed"] += 1
        return result


class QuarterlyReminderScheduler:
    """Minimal dependency-free scheduler for quarterly reminders."""

    _lock = threading.Lock()
    _started = False

    @staticmethod
    def _next_run(now, hour, allow_same_day_catch_up=False):
        quarter_month = ((now.month - 1) // 3) * 3 + 1
        current_target = datetime(now.year, quarter_month, 1, hour, 0, 0)
        if now < current_target:
            return current_target
        # A process starting later on the scheduled day should still send once.
        if allow_same_day_catch_up and now.date() == current_target.date():
            return now
        next_month = quarter_month + 3
        next_year = now.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        return datetime(next_year, next_month, 1, hour, 0, 0)

    @classmethod
    def init_app(cls, app):
        if not app.config.get("QUARTERLY_REMINDERS_ENABLED", True):
            return
        with cls._lock:
            if cls._started:
                return
            cls._started = True

        def run():
            first_iteration = True
            while True:
                now = datetime.now()
                target = cls._next_run(
                    now,
                    app.config.get("QUARTERLY_REMINDER_HOUR", 9),
                    allow_same_day_catch_up=first_iteration,
                )
                first_iteration = False
                delay = max(0.0, (target - now).total_seconds())
                if delay:
                    threading.Event().wait(delay)
                try:
                    with app.app_context():
                        QuarterlyReminderService.send_due_reminders(
                            app.config.get("PORTAL_BASE_URL", "http://127.0.0.1:5001")
                        )
                except Exception:
                    app.logger.exception("Quarterly document reminders failed")
                # Move beyond the current boundary before calculating again.
                threading.Event().wait(60)

        threading.Thread(
            target=run,
            name="quarterly-document-reminders",
            daemon=True,
        ).start()
