from flask import Blueprint, render_template, redirect, url_for
from services.auth_service import AuthService
from services.document_service import DocumentService
from data.mock_data import DASHBOARD_RECORDS, PLANTS, DEPARTMENTS

graphics_report_bp = Blueprint("graphics_report", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


def _get_statistics():
    """Calculate statistics from dashboard records for the graphics report."""
    visible_department = AuthService.get_visible_department()
    # Get records from database
    records = DocumentService.get_all_documents(access_department=visible_department)
    
    # Fallback to mock data if database is empty
    if not records:
        records = DASHBOARD_RECORDS
        if visible_department:
            records = [record for record in records if record.get("department") == visible_department]
    
    # Overall document statistics
    total_documents = len(records)
    pending_docs = len([r for r in records if r.get("approval_status") == "Pending"])
    approved_docs = len([r for r in records if r.get("approval_status") == "Approved"])
    rejected_docs = len([r for r in records if r.get("approval_status") == "Rejected"])
    
    # Plant-wise statistics
    plant_stats = {}
    for record in records:
        plant = record.get("plant", "Unknown")
        if plant not in plant_stats:
            plant_stats[plant] = {
                "total": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0,
            }
        plant_stats[plant]["total"] += 1
        status = record.get("approval_status", "Pending")
        if status == "Pending":
            plant_stats[plant]["pending"] += 1
        elif status == "Approved":
            plant_stats[plant]["approved"] += 1
        elif status == "Rejected":
            plant_stats[plant]["rejected"] += 1
    
    # Customer-wise statistics
    customer_stats = {}
    for record in records:
        customer = record.get("customer", "Unknown")
        if customer not in customer_stats:
            customer_stats[customer] = {
                "total": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0,
            }
        customer_stats[customer]["total"] += 1
        status = record.get("approval_status", "Pending")
        if status == "Pending":
            customer_stats[customer]["pending"] += 1
        elif status == "Approved":
            customer_stats[customer]["approved"] += 1
        elif status == "Rejected":
            customer_stats[customer]["rejected"] += 1
    
    # Department-wise statistics
    dept_stats = {}
    for record in records:
        dept = record.get("department", "Unknown")
        if dept not in dept_stats:
            dept_stats[dept] = {
                "total": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0,
            }
        dept_stats[dept]["total"] += 1
        status = record.get("approval_status", "Pending")
        if status == "Pending":
            dept_stats[dept]["pending"] += 1
        elif status == "Approved":
            dept_stats[dept]["approved"] += 1
        elif status == "Rejected":
            dept_stats[dept]["rejected"] += 1
    
    return {
        "overall": {
            "total": total_documents,
            "pending": pending_docs,
            "approved": approved_docs,
            "rejected": rejected_docs,
        },
        "plant": plant_stats,
        "customer": customer_stats,
        "department": dept_stats,
    }


@graphics_report_bp.route("/graphics-report")
def index():
    redir = _require_login()
    if redir:
        return redir
    
    stats = _get_statistics()
    
    return render_template(
        "graphics_report.html",
        stats=stats,
        can_manage_documents=AuthService.has_high_level_access(),
    )
