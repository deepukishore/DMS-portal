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
    """Send one relevant document-review digest per L1/L2 user each quarter."""

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
    def eligible_recipients():
        """Return L1/L2 users who have a department for document matching."""
        recipients = []
        for user in UserStoreService.get_all_users():
            email = str(user.get("email") or "").strip().lower()
            department = normalize_department(user.get("department") or "")
            qms_level = str(user.get("qms_level") or "").strip().upper()
            if user.get("role") == "Admin":
                qms_level = "L1"
            if not email or not department or qms_level not in {"L1", "L2"}:
                continue
            recipients.append({**user, "email": email, "department": department})
        return sorted(recipients, key=lambda item: item["email"])

    @staticmethod
    def documents_for_recipient(user, documents):
        """Match approved documents by department and any configured category scope."""
        department = normalize_department(user.get("department") or "").casefold()
        raw_categories = (
            user.get("document_categories")
            or user.get("categories")
            or user.get("category")
            or ""
        )
        if isinstance(raw_categories, str):
            category_scope = {
                item.strip().casefold()
                for item in raw_categories.replace(";", ",").split(",")
                if item.strip()
            }
        else:
            category_scope = {
                str(item).strip().casefold()
                for item in raw_categories
                if str(item).strip()
            }

        relevant = []
        for record in documents:
            document_department = normalize_department(
                record.get("department") or ""
            ).casefold()
            document_category = str(record.get("category") or "Uncategorized").strip()
            if document_department != department:
                continue
            if category_scope and document_category.casefold() not in category_scope:
                continue
            relevant.append(record)
        return relevant

    @staticmethod
    def _claim(quarter_key, recipient_email, attempted_at, force=False):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT status FROM quarterly_recipient_reminders WHERE quarter_key = ? AND recipient_email = ?",
                (quarter_key, recipient_email),
            )
            existing = cursor.fetchone()
            if existing and existing["status"] == "sending":
                return False
            if existing and existing["status"] == "sent" and not force:
                return False
            if existing:
                cursor.execute(
                    """
                    UPDATE quarterly_recipient_reminders
                    SET status = 'sending', attempted_at = ?, sent_at = NULL, error = NULL
                    WHERE quarter_key = ? AND recipient_email = ? AND status != 'sending'
                    """,
                    (attempted_at, quarter_key, recipient_email),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO quarterly_recipient_reminders
                        (quarter_key, recipient_email, status, attempted_at)
                    VALUES (?, ?, 'sending', ?)
                    """,
                    (quarter_key, recipient_email, attempted_at),
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
    def _finish(quarter_key, recipient_email, document_ids, error=None):
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE quarterly_recipient_reminders
            SET status = ?, sent_at = ?, document_ids = ?, error = ?
            WHERE quarter_key = ? AND recipient_email = ?
            """,
            (
                "failed" if error else "sent",
                None if error else now_text,
                json.dumps(document_ids),
                error,
                quarter_key,
                recipient_email,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def send_due_reminders(base_url, now=None, force=False):
        now = now or datetime.now()
        quarter_key = QuarterlyReminderService.quarter_key(now)
        base_url = str(base_url or "").rstrip("/")
        documents = QuarterlyReminderService.current_approved_documents()
        result = {
            "quarter": quarter_key,
            "sent": 0,
            "failed": 0,
            "skipped": 0,
            "documents": 0,
        }

        for user in QuarterlyReminderService.eligible_recipients():
            relevant_documents = QuarterlyReminderService.documents_for_recipient(
                user,
                documents,
            )
            if not relevant_documents:
                continue

            recipient_email = user["email"]
            attempted_at = now.strftime("%Y-%m-%d %H:%M:%S")
            if not QuarterlyReminderService._claim(
                quarter_key,
                recipient_email,
                attempted_at,
                force=force,
            ):
                result["skipped"] += 1
                continue

            document_ids = [int(record["id"]) for record in relevant_documents]
            result["documents"] += len(document_ids)
            sent, error = MailService.send_quarterly_document_digest(
                recipient_email,
                user.get("name") or "Colleague",
                relevant_documents,
                base_url,
            )
            QuarterlyReminderService._finish(
                quarter_key,
                recipient_email,
                document_ids,
                error=None if sent else (error or "Email delivery failed."),
            )
            if sent:
                result["sent"] += 1
                SystemLogService.log_quarterly_digest(
                    quarter_key,
                    recipient_email,
                    len(relevant_documents),
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
