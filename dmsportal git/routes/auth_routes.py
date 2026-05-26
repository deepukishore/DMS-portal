from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from data.mock_data import DEPARTMENTS, PLANTS
from services.auth_service import AuthService
from services.mail_service import MailService
from services.password_reset_service import PasswordResetService
from services.system_log_service import SystemLogService
from services.user_store_service import UserStoreService

auth_bp = Blueprint("auth", __name__)


def _get_safe_next_url():
    next_url = request.values.get("next", "").strip()
    if next_url.startswith("/"):
        return next_url
    return url_for("dashboard.index")


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = _get_safe_next_url()
    if AuthService.is_logged_in():
        return redirect(next_url)
    if request.method == "POST":
        credential = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        user = None
        error = None
        
        # Check if credential looks like a GENID (alphanumeric, typically starts with EMP)
        if credential and not '@' in credential:
            user, error = AuthService.login_by_genid(credential, password)
        
        # If GENID login failed or credential has @, try email login
        if not user and '@' in credential:
            user, error = AuthService.login(credential, password)
        elif not user and not error:
            user, error = AuthService.login(credential, password)
        
        if user:
            ip = request.remote_addr or "-"
            SystemLogService.log_login(user["email"], user["name"], ip)
            return redirect(next_url)
        flash(error or "Invalid credentials", "error")
    return render_template("auth/login.html", next_url=next_url)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if AuthService.is_logged_in():
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        emp_id = request.form.get("emp_id", "").strip()
        plant = request.form.get("plant", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html", plants=PLANTS, departments=DEPARTMENTS)
        user, error = AuthService.register(name, email, password, emp_id, plant, department)
        if user:
            ip = request.remote_addr or "-"
            SystemLogService.log_register(user["email"], user["name"], ip)
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
        flash(error, "error")
    return render_template("auth/register.html", plants=PLANTS, departments=DEPARTMENTS)


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.form.get("email", "").strip()
    if UserStoreService.email_exists(email):
        token = PasswordResetService.generate_token(email)
        reset_url = url_for("auth.reset_password", token=token, _external=True)
        ok, err = MailService.send_password_reset(email, reset_url)
        if not ok:
            print(f"[DEV] Password reset link for {email}: {reset_url}")
    flash("If that email is registered, a reset link has been sent.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email, error = PasswordResetService.verify_token(token)
    if error:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        new_password = request.form.get("password", "")
        ok, err = PasswordResetService.reset_password(email, new_password)
        if ok:
            flash("Password updated. Please log in.", "success")
            return redirect(url_for("auth.login"))
        flash(err, "error")
    return render_template("auth/reset_password.html", token=token)


@auth_bp.route("/logout")
def logout():
    email = session.get("user_email", "")
    name = session.get("user_name", "")
    if email:
        SystemLogService.log_logout(email, name)
    AuthService.logout()
    return redirect(url_for("auth.login"))
