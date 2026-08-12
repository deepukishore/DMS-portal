from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.document_library_service import DocumentLibraryService
from services.document_tracking_service import DocumentTrackingService
from data.mock_data import DASHBOARD_RECORDS, PLANTS
from data.departments import OFFICIAL_DEPARTMENTS
from data.customers import OFFICIAL_CUSTOMERS
from data.document_categories import infer_document_category

graphics_report_bp = Blueprint("graphics_report", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


def _add_status_count(bucket, record):
    status = record.get("approval_status") or "Pending"
    if DocumentService.is_pending_status(status):
        bucket["pending"] += 1
        return
    status_key = str(status).strip().lower()
    if status_key in bucket:
        bucket[status_key] += 1


def _get_records():
    visible_department = AuthService.get_visible_department()
    records = DocumentService.get_all_documents(access_department=visible_department)
    if not records:
        records = DASHBOARD_RECORDS
        if visible_department:
            records = [r for r in records if r.get("department") == visible_department]
    return records


def _get_statistics(records=None):
    records = records if records is not None else _get_records()

    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start  = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    total     = len(records)
    approved  = sum(1 for r in records if r.get("approval_status") == "Approved")
    pending   = DocumentService.count_pending(records)
    rejected  = sum(1 for r in records if r.get("approval_status") == "Rejected")

    this_month = 0
    this_week  = 0
    for r in records:
        try:
            ts = datetime.strptime(str(r.get("uploaded_at", ""))[:10], "%Y-%m-%d")
            if ts >= month_start:
                this_month += 1
            if ts >= week_start:
                this_week += 1
        except (ValueError, TypeError):
            pass

    # Per-plant stats
    plant_stats = {}
    for r in records:
        plant = r.get("plant", "Unknown")
        s = plant_stats.setdefault(plant, {"total": 0, "approved": 0, "pending": 0, "rejected": 0})
        s["total"] += 1
        _add_status_count(s, r)

    # Per-customer stats
    customer_stats = {}
    for r in records:
        cust = r.get("customer", "Unknown")
        s = customer_stats.setdefault(cust, {"total": 0, "approved": 0, "pending": 0, "rejected": 0})
        s["total"] += 1
        _add_status_count(s, r)

    # Per-department stats
    dept_stats = {}
    for r in records:
        dept = r.get("department", "Unknown")
        s = dept_stats.setdefault(dept, {"total": 0, "approved": 0, "pending": 0, "rejected": 0})
        s["total"] += 1
        _add_status_count(s, r)

    return {
        "overall": {
            "total":      total,
            "approved":   approved,
            "pending":    pending,
            "rejected":   rejected,
            "this_month": this_month,
            "this_week":  this_week,
        },
        # True master-list totals (independent of what's in documents)
        "total_plants":      len(PLANTS),
        "total_customers":   len(OFFICIAL_CUSTOMERS),
        "total_departments": len(OFFICIAL_DEPARTMENTS),
        # Per-entity breakdowns for charts
        "plant":      plant_stats,
        "customer":   customer_stats,
        "department": dept_stats,
    }


@graphics_report_bp.route("/graphics-report")
def index():
    redir = _require_login()
    if redir:
        return redir

    records = _get_records()
    stats = _get_statistics(records)
    visible_department = AuthService.get_visible_department()
    trend_data = DocumentTrackingService.get_upload_trend_data(
        days=90, access_department=visible_department
    )

    # Count the same document records used by the dashboard table. The previous
    # report counted static catalogue entries, which produced 178 versus the
    # actual 78 document records.
    categories = {
        category["key"]: category["label"]
        for category in DocumentLibraryService.get_categories()
    }
    library_stats = {
        key: {"label": label, "total": 0, "breakdown": {}}
        for key, label in categories.items()
    }
    for record in records:
        category_key = infer_document_category(record)
        label = categories[category_key]
        entry = library_stats.setdefault(
            category_key,
            {"label": label, "total": 0, "breakdown": {}},
        )
        entry["total"] += 1

    library_stats = dict(
        sorted(library_stats.items(), key=lambda item: item[1]["label"].lower())
    )

    return render_template(
        "graphics_report.html",
        stats=stats,
        trend_data=trend_data,
        library_stats=library_stats,
        can_manage_documents=AuthService.has_high_level_access(),
    )
