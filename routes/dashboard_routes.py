import csv
import mimetypes
import os
from io import StringIO
import json
from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, Response, flash, redirect, render_template, request, send_file, session, url_for, abort, current_app, jsonify

from data.mock_data import CUSTOMER_FILTERS, DEPARTMENTS, PLANTS, DASHBOARD_RECORDS
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.presentation_service import plant_code
from services.system_log_service import SystemLogService
from services.document_preview_service import DocumentPreviewService
from services.document_tracking_service import DocumentTrackingService
from services.document_library_service import DocumentLibraryService

dashboard_bp = Blueprint("dashboard", __name__)


def _record_status_counts(records):
    """Return consistent dashboard totals for the accessible record set."""
    return {
        "total": len(records),
        "pending": DocumentService.count_pending(records),
        "approved": sum(
            1 for record in records
            if record.get("approval_status") == "Approved"
        ),
        "rejected": sum(
            1 for record in records
            if record.get("approval_status") == "Rejected"
        ),
    }


def _count_by(records, field):
    """Build a stable, highest-count-first breakdown for dashboard navigation."""
    counts = Counter(
        (record.get(field) or "Not assigned").strip()
        for record in records
    )
    return [
        {"label": label, "count": count}
        for label, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )
    ]


def _count_approved_by(records, field):
    """Count only approved documents for dashboard navigation summaries."""
    approved_records = [
        record for record in records
        if (record.get("approval_status") or "") == "Approved"
    ]
    return _count_by(approved_records, field)


def _daily_upload_trend(records, days=14):
    """Return a gap-free daily upload series suitable for the dashboard chart."""
    today = datetime.now().date()
    first_day = today - timedelta(days=days - 1)
    daily_counts = Counter()

    for record in records:
        uploaded_at = str(record.get("uploaded_at") or "").strip()
        if len(uploaded_at) < 10:
            continue
        try:
            uploaded_day = datetime.strptime(uploaded_at[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        if first_day <= uploaded_day <= today:
            daily_counts[uploaded_day.isoformat()] += 1

    return [
        {
            "date": (first_day + timedelta(days=offset)).isoformat(),
            "label": (first_day + timedelta(days=offset)).strftime("%d %b"),
            "count": daily_counts[(first_day + timedelta(days=offset)).isoformat()],
        }
        for offset in range(days)
    ]


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


@dashboard_bp.route("/dashboard")
def index():
    redir = _require_login()
    if redir:
        return redir

    visible_department = AuthService.get_visible_department()
    search = request.args.get("search", "")
    plant = request.args.get("plant", "")
    department = request.args.get("department", "")
    customer = request.args.get("customer", "")
    status = request.args.get("status", "")
    page = request.args.get("page", "1")
    page_size = request.args.get("page_size", "10")

    try:
        page = max(1, int(page))
    except (ValueError, TypeError):
        page = 1

    try:
        page_size = int(page_size)
    except (ValueError, TypeError):
        page_size = 10
    page_size = page_size if page_size in (10, 25, 50, 100) else 10

    # Get all documents from database
    all_records = DocumentService.get_all_documents("", "", "", "", access_department=visible_department)
    
    # Use mock data only if database is completely empty.
    overview_records = all_records
    if not all_records:
        overview_records = list(DASHBOARD_RECORDS)
        if visible_department:
            overview_records = [
                record for record in overview_records
                if record.get("department") == visible_department
            ]
        records = list(overview_records)
        if search:
            search_lower = search.lower()
            records = [r for r in records if 
                search_lower in r.get('name', '').lower() or
                search_lower in r.get('file_name', '').lower() or
                search_lower in r.get('plant', '').lower() or
                search_lower in r.get('department', '').lower() or
                search_lower in r.get('customer', '').lower() or
                search_lower in r.get('document_number', '').lower() or
                search_lower in r.get('revision_number', '').lower() or
                search_lower in r.get('category', '').lower() or
                search_lower in r.get('uploaded_at', '').lower() or
                search_lower in r.get('approval_status', '').lower()]
        if plant:
            records = [r for r in records if r.get('plant') == plant]
        if department and not visible_department:
            records = [r for r in records if r.get('department') == department]
        if customer:
            records = [r for r in records if r.get('customer') == customer]
    else:
        records = DocumentService.get_all_documents(search, plant, department, customer, access_department=visible_department)

    if status:
        records = DocumentService.filter_by_status(records, status)

    total_records = len(records)
    page_count = max(1, (total_records + page_size - 1) // page_size)
    page = min(max(page, 1), page_count)
    page_records = records[(page - 1) * page_size: page * page_size] if total_records else []

    dashboard_overview = _record_status_counts(overview_records)
    plant_counts = _count_approved_by(overview_records, "plant")
    department_counts = _count_by(overview_records, "department")
    plant_count_map = {item["label"]: item["count"] for item in plant_counts}
    daily_trend = _daily_upload_trend(overview_records)
    library_stats = DocumentLibraryService.get_dashboard_statistics(
        qms_level=AuthService.get_qms_level(),
        access_department=visible_department,
    )
    library_total = sum(item["count"] for item in library_stats)
    plant_library_total = sum(
        item["count"] for item in library_stats
        if item["key"] in {"qms", "core_tools_manuals", "eohms", "awards_certifications"}
    )
    customer_library_total = sum(
        item["count"] for item in library_stats
        if item["key"] in {"csr", "customer_score_card"}
    )
    
    # Pop the one-time welcome flag set on login
    show_welcome = session.pop('show_welcome', False)
    
    # Get user data for recently viewed and bookmarks
    user_email = session.get('user_email', '')
    recently_viewed = DocumentTrackingService.get_recently_viewed(user_email, limit=5, access_department=visible_department) if user_email else []
    bookmarks = DocumentTrackingService.get_bookmarks(user_email, access_department=visible_department) if user_email else []

    return render_template(
        "dashboard.html",
        records=records,
        page_records=page_records,
        total_records=total_records,
        page=page,
        page_size=page_size,
        page_count=page_count,
        plants=PLANTS,
        departments=DEPARTMENTS,
        customers=CUSTOMER_FILTERS,
        search=search,
        selected_plant=plant,
        selected_dept=department,
        selected_customer=customer,
        selected_status=status,
        can_manage_documents=AuthService.has_high_level_access(),
        can_access_admin_sections=AuthService.has_high_level_access(),
        pending_count=dashboard_overview["pending"],
        pending_statuses=DocumentService.PENDING_APPROVAL_STATUSES,
        dashboard_overview=dashboard_overview,
        plant_counts=plant_counts,
        plant_count_map=plant_count_map,
        department_counts=department_counts,
        daily_trend=daily_trend,
        library_stats=library_stats,
        library_total=library_total,
        plant_library_total=plant_library_total,
        customer_library_total=customer_library_total,
        recently_viewed=recently_viewed,
        bookmarks=bookmarks,
        show_welcome=show_welcome,
    )


@dashboard_bp.route("/dashboard/export")
def export_documents():
    redir = _require_login()
    if redir:
        return redir

    visible_department = AuthService.get_visible_department()
    records = DocumentService.get_all_documents(
        request.args.get("search", ""),
        request.args.get("plant", ""),
        request.args.get("department", ""),
        request.args.get("customer", ""),
        access_department=visible_department,
    )
    records = DocumentService.filter_by_status(
        records,
        request.args.get("status", ""),
    )

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Uploaded By",
            "User ID",
            "Plant",
            "Department",
            "Customer",
            "Document Number",
            "Revision Number",
            "Category",
            "File Name",
            "Uploaded Date",
            "Approval Status",
        ]
    )
    for record in records:
        writer.writerow(
            [
                record["name"],
                record["user_id"],
                plant_code(record["plant"]),
                record["department"],
                record.get("customer", ""),
                record.get("document_number", ""),
                record.get("revision_number", ""),
                record.get("category", ""),
                record["file_name"],
                record["uploaded_at"],
                record.get("approval_status", "Pending"),
            ]
        )

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=master-dashboard-export.csv"},
    )


@dashboard_bp.route("/dashboard/delete/<int:doc_id>", methods=["POST"])
def delete_document(doc_id):
    redir = _require_login()
    if redir:
        return redir
    if not AuthService.has_high_level_access():
        flash("Only admins and higher-level users can delete documents.", "error")
        return redirect(url_for("dashboard.index"))

    removed, error = DocumentService.delete_document(doc_id)
    if removed:
        SystemLogService.log_delete(
            session["user_email"],
            session["user_name"],
            removed["file_name"],
            removed["plant"],
            removed["department"],
        )
        flash(f'"{removed["file_name"]}" deleted successfully.', "success")
    else:
        flash(error, "error")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/dashboard/view/<int:doc_id>")
def view_document(doc_id):
    redir = _require_login()
    if redir:
        return redir

    document = DocumentService.get_document_by_id(doc_id, access_department=AuthService.get_visible_department())
    if not document:
        flash("Document not found.", "error")
        return redirect(url_for("dashboard.index"))

    # Track recently viewed
    user_email = session.get('user_email', '')
    if user_email:
        DocumentTrackingService.track_recently_viewed(user_email, doc_id)
        is_bookmarked = DocumentTrackingService.is_bookmarked(user_email, doc_id)
    else:
        is_bookmarked = False

    # Prefer the generated PDF viewing copy, with the original as a fallback.
    preview_path = DocumentService.get_preview_file_path(
        document,
        current_app.config["UPLOAD_FOLDER"],
    )
    file_exists = os.path.exists(preview_path)
    view_file_url = url_for("dashboard.view_file", doc_id=doc_id)
    preview = (
        DocumentPreviewService.build_preview(preview_path, view_file_url)
        if file_exists
        else {"mode": "missing"}
    )

    SystemLogService.log_view(
        session["user_email"],
        session["user_name"],
        document["file_name"],
        f"{document['plant']} / {document['department']}",
    )

    return render_template(
        "document_view.html",
        record=document,
        file_exists=file_exists,
        preview=preview,
        is_bookmarked=is_bookmarked,
    )


@dashboard_bp.route("/document-view")
def view_document_by_file():
    redir = _require_login()
    if redir:
        return redir

    file_name = request.args.get("file", "").strip()
    if not file_name:
        flash("No file was selected for viewing.", "error")
        return redirect(url_for("dashboard.index"))

    document = DocumentService.get_document_by_file_name(
        file_name,
        access_department=AuthService.get_visible_department(),
    )
    if not document:
        flash(f'"{file_name}" is not available as an uploaded document yet.', "error")
        return redirect(url_for("dashboard.index"))

    return redirect(url_for("dashboard.view_document", doc_id=document["id"]))


@dashboard_bp.route("/dashboard/view/<int:doc_id>/file")
def view_file(doc_id):
    redir = _require_login()
    if redir:
        return redir

    document = DocumentService.get_document_by_id(doc_id, access_department=AuthService.get_visible_department())
    if not document:
        abort(404)

    file_path = DocumentService.get_preview_file_path(
        document,
        current_app.config["UPLOAD_FOLDER"],
    )
    if not os.path.exists(file_path):
        abort(404)

    if not DocumentPreviewService.can_stream_inline(file_path):
        abort(404)

    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"
    response = send_file(file_path, mimetype=mime_type, as_attachment=False)
    response.headers["Content-Disposition"] = f'inline; filename="{os.path.basename(file_path)}"'
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@dashboard_bp.route("/api/bookmark/<int:doc_id>", methods=["POST"])
def toggle_bookmark(doc_id):
    """Toggle bookmark for a document."""
    redir = _require_login()
    if redir:
        return redir
    
    user_email = session.get('user_email', '')
    if not user_email:
        return jsonify({'error': 'Not logged in'}), 401
    
    document = DocumentService.get_document_by_id(doc_id, access_department=AuthService.get_visible_department())
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    is_bookmarked = DocumentTrackingService.toggle_bookmark(user_email, doc_id)
    
    return jsonify({
        'success': True,
        'is_bookmarked': is_bookmarked,
        'document_id': doc_id
    })


@dashboard_bp.route("/api/trend-data")
def get_trend_data():
    """Get upload trend data for chart."""
    redir = _require_login()
    if redir:
        return redir
    
    days = request.args.get('days', 90, type=int)
    trend_data = DocumentTrackingService.get_upload_trend_data(days, access_department=AuthService.get_visible_department())
    
    return jsonify(trend_data)

@dashboard_bp.route('/api/preview-url')
def get_preview_url():
    redir = _require_login()
    if redir:
        return redir

    file_name = request.args.get('file', '').strip()
    if not file_name:
        return jsonify({'url': ''})

    document = DocumentService.get_document_by_file_name(
        file_name,
        access_department=AuthService.get_visible_department(),
    )
    if not document:
        return jsonify({'url': ''})

    return jsonify({'url': url_for('dashboard.view_file', doc_id=document['id'])})
