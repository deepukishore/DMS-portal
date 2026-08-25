import os
import re
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from services.auth_service import AuthService
from services.system_log_service import SystemLogService
from services.user_store_service import UserStoreService

profile_bp = Blueprint("profile", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


@profile_bp.route("/profile", methods=["GET"])
def index():
    redir = _require_login()
    if redir:
        return redir

    current_user = AuthService.get_current_user()
    all_user_logs = SystemLogService.get_logs_by_user(session["user_email"])
    log_search = request.args.get("log_search", "").strip()
    selected_log_action = request.args.get("log_action", "").strip()
    log_page = max(1, request.args.get("log_page", 1, type=int))
    log_page_size = request.args.get("log_page_size", 10, type=int)
    if log_page_size not in (10, 25, 50):
        log_page_size = 10

    log_actions = sorted({
        log.get("action_type", "")
        for log in all_user_logs
        if log.get("action_type")
    })
    filtered_logs = all_user_logs
    if selected_log_action:
        filtered_logs = [
            log for log in filtered_logs
            if log.get("action_type", "") == selected_log_action
        ]
    if log_search:
        search_term = log_search.casefold()
        filtered_logs = [
            log for log in filtered_logs
            if search_term in " ".join((
                str(log.get("timestamp", "")),
                str(log.get("action_type", "")),
                str(log.get("details", "")),
            )).casefold()
        ]

    filtered_log_count = len(filtered_logs)
    log_page_count = max(1, (filtered_log_count + log_page_size - 1) // log_page_size)
    log_page = min(log_page, log_page_count)
    log_start = (log_page - 1) * log_page_size
    user_logs = filtered_logs[log_start:log_start + log_page_size]
    if current_user.get("avatar"):
        session["user_avatar"] = current_user["avatar"]

    return render_template(
        "profile.html",
        current_user=current_user,
        user_logs=user_logs,
        total_user_logs=len(all_user_logs),
        filtered_log_count=filtered_log_count,
        log_actions=log_actions,
        log_search=log_search,
        selected_log_action=selected_log_action,
        log_page=log_page,
        log_page_size=log_page_size,
        log_page_count=log_page_count,
    )


@profile_bp.route("/profile/upload-avatar", methods=["POST"])
def upload_avatar():
    redir = _require_login()
    if redir:
        return redir

    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("profile.index"))

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        flash("Only image files are allowed.", "error")
        return redirect(url_for("profile.index"))

    from flask import current_app
    avatar_dir = os.path.join(current_app.static_folder, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)

    filename = secure_filename(f"{session['user_id']}{ext}")
    file.save(os.path.join(avatar_dir, filename))
    UserStoreService.update_avatar(session["user_email"], filename)
    session["user_avatar"] = filename
    flash("Profile photo updated.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/update", methods=["POST"])
def update_profile():
    redir = _require_login()
    if redir:
        return redir

    name = request.form.get("name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    if not name:
        flash("Full name is required.", "error")
        return redirect(url_for("profile.index"))

    if mobile and not re.match(r'^[0-9()+\-\s]{6,20}$', mobile):
        flash("Please enter a valid mobile number using digits, +, -, spaces, or parentheses.", "error")
        return redirect(url_for("profile.index"))

    updated_user = UserStoreService.update_user_profile(
        session["user_email"],
        name=name,
        mobile=mobile,
    )
    if updated_user:
        session["user_name"] = updated_user.get("name", name)
        session["user_mobile"] = updated_user.get("mobile", "")

    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/update-password", methods=["POST"])
def update_password():
    redir = _require_login()
    if redir:
        return redir

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "error")
        return redirect(url_for("profile.index"))

    current_user = AuthService.get_current_user()
    if not check_password_hash(current_user["password_hash"], current_password):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("profile.index"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("profile.index"))

    if len(new_password) < 8:
        flash("New password must be at least 8 characters.", "error")
        return redirect(url_for("profile.index"))

    UserStoreService.update_password(session["user_email"], generate_password_hash(new_password))
    SystemLogService.log_password_change(session["user_email"], session["user_name"])
    flash("Password updated successfully.", "success")
    return redirect(url_for("profile.index"))
