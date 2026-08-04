from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.document_library_service import DocumentLibraryService
from services.document_tracking_service import DocumentTrackingService
from data.mock_data import DASHBOARD_RECORDS, PLANTS
from data.departments import OFFICIAL_DEPARTMENTS
from data.customers import OFFICIAL_CUSTOMERS

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


def _get_statistics():
    visible_department = AuthService.get_visible_department()
    records = DocumentService.get_all_documents(access_department=visible_department)
    if not records:
        records = DASHBOARD_RECORDS
        if visible_department:
            records = [r for r in records if r.get("department") == visible_department]

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

    stats = _get_statistics()
    visible_department = AuthService.get_visible_department()
    trend_data = DocumentTrackingService.get_upload_trend_data(
        days=90, access_department=visible_department
    )

    # Document library statistics and breakdown per category / subfolder
    def _collect_library_breakdown():
        breakdown = {}
        qms_level = AuthService.get_qms_level() if hasattr(AuthService, 'get_qms_level') else ''
        categories = DocumentLibraryService.get_categories()
        for cat in categories:
            key = cat.get('key')
            label = cat.get('label')
            data = DocumentLibraryService.get_client_category_data(key, qms_level=qms_level, access_department=visible_department)
            total = len(DocumentLibraryService._collect_document_files(data))
            entry = {'label': label, 'total': total, 'breakdown': {}}

            # QMS: show groups and subfolders
            if key == 'qms':
                groups = data.get('document_groups', {})
                for gk, gv in groups.items():
                    gcount = len(DocumentLibraryService._collect_document_files(gv))
                    sub = {'total': gcount, 'subfolders': {}}
                    sec = gv.get('secondary_options') or gv.get('plant_departments') or {}
                    if sec:
                        for sk, sv in sec.items():
                            scount = len(DocumentLibraryService._collect_document_files(sv))
                            sub['subfolders'][sk] = {'label': sv.get('label') or sk, 'total': scount}
                    entry['breakdown'][gk] = sub

            # primary_options style categories (CSR, Core tools, Awards)
            elif 'primary_options' in data:
                opts = data.get('primary_options', {})
                for pk, pv in opts.items():
                    pcount = len(DocumentLibraryService._collect_document_files(pv))
                    entry['breakdown'][pk] = {'label': pv.get('label') or pk, 'total': pcount}

            # flat categories with files only
            else:
                # no extra breakdown
                pass

            breakdown[key] = entry
        return breakdown

    library_stats = _collect_library_breakdown()

    return render_template(
        "graphics_report.html",
        stats=stats,
        trend_data=trend_data,
        library_stats=library_stats,
        can_manage_documents=AuthService.has_high_level_access(),
    )
