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
    user_logs = SystemLogService.get_logs_by_user(session["user_email"])
    if current_user.get("avatar"):
        session["user_avatar"] = current_user["avatar"]

    return render_template("profile.html", current_user=current_user, user_logs=user_logs)


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

    mobile = request.form.get("mobile", "").strip()
    if mobile and not re.match(r'^[0-9()+\-\s]{6,20}$', mobile):
        flash("Please enter a valid mobile number using digits, +, -, spaces, or parentheses.", "error")
        return redirect(url_for("profile.index"))

    updated_user = UserStoreService.update_user_profile(
        session["user_email"],
        mobile=mobile,
    )
    if updated_user:
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
