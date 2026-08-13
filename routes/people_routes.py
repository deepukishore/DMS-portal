from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from services.auth_service import AuthService
from services.system_log_service import SystemLogService
from services.user_store_service import UserStoreService

people_bp = Blueprint("people", __name__)


@people_bp.route("/people")
def index():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    if not AuthService.has_high_level_access():
        return redirect(url_for("dashboard.index"))

    users = UserStoreService.get_all_users()
    level_counts = {
        level: sum(1 for user in users if user.get("qms_level", "L4") == level)
        for level in ("L1", "L2", "L3", "L4")
    }
    return render_template(
        "people.html",
        users=users,
        level_counts=level_counts,
        can_edit_qms_levels=AuthService.is_admin(),
    )


@people_bp.route("/people/qms-level", methods=["POST"])
def update_qms_level():
    if not AuthService.is_logged_in():
        return jsonify({"ok": False, "message": "Please sign in again."}), 401
    if not AuthService.is_admin():
        return jsonify({
            "ok": False,
            "message": "Only an administrator can update QMS levels.",
        }), 403

    payload = request.get_json(silent=True) or request.form
    email = str(payload.get("email", "")).strip().lower()
    qms_level = str(payload.get("qms_level", "")).strip().upper()
    if not email:
        return jsonify({"ok": False, "message": "Select a user to update."}), 400

    existing = UserStoreService.get_user_by_email(email)
    if not existing:
        return jsonify({"ok": False, "message": "User not found."}), 404

    previous_level = existing.get("qms_level") or "L4"
    try:
        updated = UserStoreService.update_qms_level(email, qms_level)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    if not updated:
        return jsonify({"ok": False, "message": "User not found."}), 404

    SystemLogService.log_qms_level_change(
        session.get("user_email", ""),
        session.get("user_name", "Administrator"),
        email,
        previous_level,
        updated["qms_level"],
    )
    return jsonify({
        "ok": True,
        "message": f'QMS level updated to {updated["qms_level"]}.',
        "user": {
            "email": updated["email"],
            "name": updated["name"],
            "qms_level": updated["qms_level"],
        },
    })
