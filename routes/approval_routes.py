import csv
import mimetypes
import os
from io import StringIO
from datetime import datetime

from itsdangerous import BadSignature
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from services.auth_service import AuthService
from services.document_service import DocumentService
from services.mail_service import MailService
from services.document_preview_service import DocumentPreviewService
from services.notification_service import NotificationService
from services.system_log_service import SystemLogService
from services.user_store_service import UserStoreService

approval_bp = Blueprint("approvals", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login", next=request.path))
    return None


def _can_decide_record(record, user=None):
    user = user or AuthService.get_current_user()
    status = record.get("approval_status", "Pending")
    if status == "Pending":
        return AuthService.is_qms_first_approver(user)
    if status == "Pending Final Approval":
        return AuthService.is_qms_final_approver(user)
    return False


def _records_with_tokens(records):
    return [
        {
            **record,
            "review_token": DocumentService.generate_review_token(
                record["id"],
                current_app.config["SECRET_KEY"],
                current_app.config["REVIEW_TOKEN_SALT"],
            ),
        }
        for record in records
    ]


def _resolve_record_or_none(token):
    access_department = AuthService.get_visible_department()
    try:
        return DocumentService.resolve_review_token(
            token,
            current_app.config["SECRET_KEY"],
            current_app.config["REVIEW_TOKEN_SALT"],
            access_department=access_department,
        )
    except (BadSignature, KeyError, TypeError):
        return None


@approval_bp.route("/approvals")
def index():
    redir = _require_login()
    if redir:
        return redir

    status = request.args.get("status", "")
    search = request.args.get("search", "")
    page = max(1, request.args.get("page", 1, type=int))
    page_size = request.args.get("page_size", 10, type=int)
    if page_size not in (10, 25, 50, 100):
        page_size = 10

    records = DocumentService.get_all_documents(
        search=search,
        access_department=AuthService.get_visible_department(),
    )
    records = DocumentService.filter_by_status(records, status)

    total = len(records)
    import math
    page_count = max(1, math.ceil(total / page_size))
    page = min(page, page_count)
    page_records = _records_with_tokens(records[(page - 1) * page_size: page * page_size])

    return render_template(
        "approvals.html",
        records=records,
        page_records=page_records,
        selected_status=status,
        search=search,
        page=page,
        page_size=page_size,
        page_count=page_count,
        total_records=total,
        pending_statuses=DocumentService.PENDING_APPROVAL_STATUSES,
    )


@approval_bp.route("/approvals/export")
def export_records():
    redir = _require_login()
    if redir:
        return redir

    status = request.args.get("status", "")
    search = request.args.get("search", "")
    records = DocumentService.get_all_documents(
        search=search,
        access_department=AuthService.get_visible_department(),
    )
    records = DocumentService.filter_by_status(records, status)

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Uploaded Date",
            "File Name",
            "Document Number",
            "Revision Number",
            "Category",
            "Plant",
            "Department",
            "Customer",
            "Status",
        ]
    )
    for record in records:
        writer.writerow(
            [
                record["uploaded_at"],
                record["file_name"],
                record.get("document_number", ""),
                record.get("revision_number", ""),
                record.get("category", ""),
                record["plant"],
                record["department"],
                record.get("customer", ""),
                record.get("approval_status", "Pending"),
            ]
        )

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=approvals-export.csv"},
    )


@approval_bp.route("/approvals/review/<token>")
def review_document(token):
    redir = _require_login()
    if redir:
        return redir

    record = _resolve_record_or_none(token)
    if not record:
        return render_template("approval_review.html", invalid_link=True), 404

    file_path = DocumentService.get_file_path(record, current_app.config["UPLOAD_FOLDER"])
    file_exists = os.path.exists(file_path)
    review_file_url = url_for("approvals.review_file", token=token)
    preview = (
        DocumentPreviewService.build_preview(file_path, review_file_url)
        if file_exists
        else {"mode": "missing"}
    )

    return render_template(
        "approval_review.html",
        invalid_link=False,
        record=record,
        token=token,
        file_exists=file_exists,
        review_file_url=review_file_url,
        preview=preview,
        can_decide=_can_decide_record(record),
    )


@approval_bp.route("/approvals/review/<token>/file")
def review_file(token):
    redir = _require_login()
    if redir:
        return redir

    record = _resolve_record_or_none(token)
    if not record:
        abort(404)

    file_path = DocumentService.get_file_path(record, current_app.config["UPLOAD_FOLDER"])
    if not os.path.exists(file_path):
        abort(404)
    if not DocumentPreviewService.can_stream_inline(file_path):
        abort(404)

    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"
    # as_attachment=False tells the browser to attempt to display the file inline
    response = send_file(file_path, mimetype=mime_type, as_attachment=False)
    
    # Explicitly set headers to enforce inline viewing and reduce caching
    response.headers["Content-Disposition"] = f'inline; filename="{os.path.basename(file_path)}"'
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@approval_bp.route("/approvals/review/<token>/decision", methods=["POST"])
def update_decision(token):
    if not AuthService.is_logged_in():
        message = "Please sign in as an admin to review this document."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": message}), 401
        return redirect(url_for("auth.login", next=request.path))

    record = _resolve_record_or_none(token)
    if not record:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": "Invalid review link."}), 404
        return render_template("approval_review.html", invalid_link=True), 404

    current_user = AuthService.get_current_user()
    record_status = record.get("approval_status", "Pending")
    if not _can_decide_record(record, current_user):
        message = (
            "Only a designated first-stage reviewer can complete this approval."
            if record_status == "Pending"
            else "Only a designated final reviewer can complete this approval."
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": message}), 403
        flash(message, "error")
        return redirect(url_for("approvals.review_document", token=token))

    status = request.form.get("status", "")
    if status not in {"Approved", "Rejected", "First Approved"}:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": "Please choose a valid approval action."}), 400
        flash("Please choose a valid approval action.", "error")
        return redirect(url_for("approvals.review_document", token=token))
    if record_status == "Pending" and status not in {"First Approved", "Rejected"}:
        message = "A designated first-stage reviewer must approve or reject this request."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": message}), 400
        flash(message, "error")
        return redirect(url_for("approvals.review_document", token=token))
    if record_status == "Pending Final Approval" and status not in {"Approved", "Rejected"}:
        message = "A designated final reviewer must approve or reject this request."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": message}), 400
        flash(message, "error")
        return redirect(url_for("approvals.review_document", token=token))

    rejection_comment = request.form.get("rejection_comment", "").strip()
    selected_recipients = request.form.get("selected_recipients", "").strip()
    if status == "Rejected" and not rejection_comment:
        message = "Please add rejection comments so the uploader knows what to fix."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": message}), 400
        flash(message, "error")
        return redirect(url_for("approvals.review_document", token=token))
    if status == "First Approved" and not selected_recipients:
        message = "Please add selected recipients or department heads before sending to final approval."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": message}), 400
        flash(message, "error")
        return redirect(url_for("approvals.review_document", token=token))

    decision_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    updated_record, error = DocumentService.update_approval_status(
        record["id"],
        status,
        rejection_comment=rejection_comment,
        decided_by=current_user.get("name", "Approver"),
        selected_recipients=selected_recipients,
    )
    if error:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": error}), 400
        flash(error, "error")
        return redirect(url_for("approvals.review_document", token=token))

    SystemLogService.log_approval_decision(
        current_user.get("email", current_app.config["APPROVAL_RECIPIENT"]),
        updated_record["file_name"],
        updated_record.get("approval_status", status),
        current_user.get("name", "Approver"),
    )
    
    # Send notification email to uploader after final decisions only.
    uploader_email = updated_record.get("uploader_email", "")
    effective_status = updated_record.get("approval_status", status)
    flash_category = "success" if effective_status == "Approved" else "warning"
    message = f"Document marked as {effective_status}."
    if status == "First Approved":
        message = "First approval accepted. Document moved to final approval."
        final_approvers = UserStoreService.get_users_by_qms_level("L1")
        final_approver_emails = [user.get("email") for user in final_approvers if user.get("email")]
        if not final_approver_emails and current_app.config["APPROVAL_RECIPIENT"]:
            final_approver_emails = [current_app.config["APPROVAL_RECIPIENT"]]
        review_url = url_for("approvals.review_document", token=token, _external=True)
        final_sent, final_error = MailService.send_document_approval_request(
            final_approver_emails,
            review_url,
            updated_record,
        )
        NotificationService.notify_qms_level(
            "L1",
            "Final approval required",
            f'{updated_record.get("original_file_name", updated_record["file_name"])} is pending final approval.',
            link_url=url_for("approvals.review_document", token=token),
            notification_type="warning",
        )
        if final_sent:
            for recipient in final_approver_emails:
                SystemLogService.log_approval_email(recipient, updated_record["file_name"])
        else:
            message = f"First approval accepted, but final approver email failed: {final_error}"
            flash_category = "warning"

    if uploader_email and status != "First Approved":
        uploader_sent, uploader_error = MailService.send_approval_decision_notification(
            uploader_email,
            updated_record,
            status,
            decision_time,
            rejection_comment=rejection_comment,
        )
        if not uploader_sent:
            message = f"Document marked as {status}, but uploader notification email failed: {uploader_error}"
            flash_category = "warning"
        else:
            message = f"Document marked as {status}. Uploader notified via email."
        NotificationService.create_notification(
            uploader_email,
            f"Document {status}",
            rejection_comment if status == "Rejected" and rejection_comment else f'{updated_record["original_file_name"] or updated_record["file_name"]} was {status.lower()}.',
            link_url=url_for("dashboard.view_document", doc_id=updated_record["id"]),
            notification_type="warning" if status == "Rejected" else "success",
        )

    if status == "Approved":
        recipients = [
            item.strip()
            for item in (updated_record.get("selected_recipients") or "").replace(";", ",").split(",")
            if item.strip() and "@" in item
        ]
        if recipients:
            selected_sent, selected_error = MailService.send_final_shared_notification(
                recipients,
                updated_record,
                decision_time,
            )
            if not selected_sent:
                message = f"Document approved, but selected-recipient email failed: {selected_error}"
                flash_category = "warning"

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {
                "ok": True,
                "doc_id": updated_record["id"],
                "status": effective_status,
                "message": message,
                "flash_category": flash_category,
                "approval_updated_at": updated_record.get("approval_updated_at", decision_time),
                "rejection_comment": updated_record.get("rejection_comment", ""),
            }
        )

    flash(message, flash_category)
    
    return redirect(url_for("approvals.review_document", token=token))


@approval_bp.route("/approvals/bulk-decision", methods=["POST"])
def bulk_update_decision():
    if not AuthService.is_logged_in():
        return jsonify({"ok": False, "message": "Please sign in."}), 401

    return jsonify({
        "ok": False,
        "message": "Bulk decisions are disabled because approvals require first-stage review, recipient selection, and final review.",
    }), 400
