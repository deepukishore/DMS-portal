from flask import Blueprint, jsonify, redirect, session, url_for

from services.auth_service import AuthService
from services.notification_service import NotificationService

notification_bp = Blueprint("notifications", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


@notification_bp.route("/notifications/mark-read/<int:notification_id>", methods=["POST"])
def mark_read(notification_id):
    redir = _require_login()
    if redir:
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    ok = NotificationService.mark_read(session["user_email"], notification_id)
    return jsonify({"ok": ok})


@notification_bp.route("/notifications/mark-all-read", methods=["POST"])
def mark_all_read():
    redir = _require_login()
    if redir:
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    updated = NotificationService.mark_all_read(session["user_email"])
    return jsonify({"ok": True, "updated": updated})
