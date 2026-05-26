from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from services.auth_service import AuthService
from services.customer_record_service import CustomerRecordService
from services.system_log_service import SystemLogService

customer_records_bp = Blueprint("customer_records", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


@customer_records_bp.route("/customer-records")
def index():
    redir = _require_login()
    if redir:
        return redir
    customers = CustomerRecordService.get_all_customers(access_department=AuthService.get_visible_department())
    return render_template("customer_records.html", customers=customers)


@customer_records_bp.route("/customer-records/files")
def get_files():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Unauthorized"}), 401
    customer = request.args.get("customer", "")
    files = CustomerRecordService.get_files_for_customer(customer, access_department=AuthService.get_visible_department())
    return jsonify({"files": files})


@customer_records_bp.route("/customer-records/view", methods=["POST"])
def view_file():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    file_name = data.get("file_name", "")
    customer = data.get("customer", "")
    SystemLogService.log_view(
        session["user_email"],
        session["user_name"],
        file_name,
        f"Customer Records - {customer}",
    )
    return jsonify({"ok": True})
