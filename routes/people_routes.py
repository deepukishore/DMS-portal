from flask import Blueprint, redirect, render_template, url_for
from services.auth_service import AuthService
from services.user_store_service import UserStoreService

people_bp = Blueprint("people", __name__)


@people_bp.route("/people")
def index():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    if not AuthService.is_admin():
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
    )
