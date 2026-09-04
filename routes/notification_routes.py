from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for

from services.auth_service import AuthService
from services.mail_service import MailService
from services.notification_service import NotificationService
from services.system_log_service import SystemLogService
from services.user_store_service import UserStoreService

notification_bp = Blueprint("notifications", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


PORTAL_UPDATE_DESTINATIONS = (
    ("", "Notification only"),
    ("/dashboard", "Dashboard"),
    ("/document-library", "Document Library"),
    ("/approvals", "Approval Queue"),
    ("/about", "About the Portal"),
)


@notification_bp.route("/notifications/portal-updates", methods=["GET", "POST"])
def portal_updates():
    redir = _require_login()
    if redir:
        return redir
    if not AuthService.is_admin():
        return "Only an administrator can publish portal updates.", 403

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        link_url = request.form.get("link_url", "").strip()
        valid_destinations = {value for value, _label in PORTAL_UPDATE_DESTINATIONS}

        if not title or not message:
            flash("Update title and details are required.", "error")
        elif len(title) > 120:
            flash("Update title must be 120 characters or fewer.", "error")
        elif len(message) > 1000:
            flash("Update details must be 1,000 characters or fewer.", "error")
        elif link_url not in valid_destinations:
            flash("Please select a valid portal destination.", "error")
        else:
            recipient_count = NotificationService.notify_all_users(
                title,
                message,
                link_url=link_url,
                notification_type="portal_update",
            )
            email_recipients = sorted({
                str(user.get("email") or "").strip().lower()
                for user in UserStoreService.get_all_users()
                if str(user.get("email") or "").strip()
            })
            portal_base_url = (
                current_app.config.get("PORTAL_BASE_URL") or request.url_root
            ).rstrip("/")
            action_url = f"{portal_base_url}{link_url or '/dashboard'}"
            email_sent, email_error = MailService.send_portal_update(
                email_recipients,
                title,
                message,
                action_url,
            )
            SystemLogService.log_portal_update(
                session.get("user_email", ""),
                session.get("user_name", "Administrator"),
                title,
                recipient_count,
            )
            flash(
                f"Portal update published to {recipient_count} registered user(s)."
                + (
                    f" Email notification sent to {len(email_recipients)} user(s)."
                    if email_sent else ""
                ),
                "success",
            )
            if not email_sent:
                flash(
                    f"The portal update was published, but email delivery failed: {email_error}",
                    "warning",
                )
            return redirect(url_for("notifications.portal_updates"))

    return render_template(
        "portal_updates.html",
        destinations=PORTAL_UPDATE_DESTINATIONS,
    )


@notification_bp.route("/notifications/mark-read/<int:notification_id>", methods=["POST"])
def mark_read(notification_id):
    redir = _require_login()
    if redir:
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    ok = NotificationService.mark_read(session["user_email"], notification_id)
    return jsonify({"ok": ok})


@notification_bp.route("/notifications/popup-seen/<int:notification_id>", methods=["POST"])
def mark_popup_seen(notification_id):
    redir = _require_login()
    if redir:
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    ok = NotificationService.mark_popup_seen(session["user_email"], notification_id)
    return jsonify({"ok": ok})


@notification_bp.route("/notifications/mark-all-read", methods=["POST"])
def mark_all_read():
    redir = _require_login()
    if redir:
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    updated = NotificationService.mark_all_read(session["user_email"])
    return jsonify({"ok": True, "updated": updated})


@notification_bp.route("/notifications/clear-all", methods=["POST"])
def clear_all():
    redir = _require_login()
    if redir:
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    deleted = NotificationService.clear_all(session["user_email"])
    return jsonify({"ok": True, "deleted": deleted})
