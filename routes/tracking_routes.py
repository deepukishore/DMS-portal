from flask import Blueprint, redirect, render_template, request, url_for

from services.auth_service import AuthService
from services.approval_tracking_service import ApprovalTrackingService
from services.document_service import DocumentService

tracking_bp = Blueprint("tracking", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login", next=request.path))
    return None


@tracking_bp.route("/tracking")
def index():
    redir = _require_login()
    if redir:
        return redir

    current_user = AuthService.get_current_user()
    user_email = (current_user or {}).get("email", "")

    search = request.args.get("search", "")
    status = request.args.get("status", "")
    scope = request.args.get("scope", "mine")
    can_view_all = AuthService.has_high_level_access(current_user)
    if scope == "all" and not can_view_all:
        scope = "mine"

    records = DocumentService.get_all_documents(
        search=search,
        access_department=AuthService.get_visible_department(current_user),
    )

    if scope == "mine" and user_email:
        records = [r for r in records if r.get("uploader_email") == user_email]
    records = DocumentService.filter_by_status(records, status)

    trackers = ApprovalTrackingService.build_trackers(records)
    summary = ApprovalTrackingService.summarize(trackers)

    return render_template(
        "approval_tracking.html",
        trackers=trackers,
        summary=summary,
        search=search,
        selected_status=status,
        scope=scope,
        can_view_all=can_view_all,
    )
