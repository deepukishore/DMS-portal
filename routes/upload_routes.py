from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for, jsonify

from data.mock_data import CUSTOMERS, PLANTS, DEPARTMENTS
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.category_document_service import CategoryDocumentService
from services.document_library_service import DocumentLibraryService
from services.mail_service import MailService
from services.notification_service import NotificationService
from services.system_log_service import SystemLogService
from services.revision_history_service import RevisionHistoryService
from services.user_store_service import UserStoreService

upload_bp = Blueprint("upload", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


def _upload_error(message, redirect_endpoint="upload.index", status_code=400):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': False, 'message': message}), status_code
    flash(message, "error")
    return redirect(url_for(redirect_endpoint))


@upload_bp.route("/upload", methods=["GET", "POST"])
def index():
    redir = _require_login()
    if redir:
        return redir

    current_user = AuthService.get_current_user()

    if request.method == "POST":
        # Allow overriding plant/department from the form selects; fall back to profile values
        plant = request.form.get('plant') or (current_user or {}).get("plant", "")
        department = request.form.get('department') or (current_user or {}).get("department", "")
        customer = request.form.get("customer", "")
        document_number = request.form.get("document_number", "").strip()
        revision_number = request.form.get("revision_number", "").strip()
        category = request.form.get("category", "").strip()
        doc_type = request.form.get("doc_type", "external")
        files = request.files.getlist("files")
        upload_target = request.form.get('upload_target', 'library')
        library_category = category

        if not plant or not department:
            return _upload_error("Your profile is missing plant or department details. Please contact an admin.")

        # If internal document, customer is optional
        if doc_type == "internal":
            customer = "Internal"
        elif not customer:
            return _upload_error("Please select a customer or mark the document as internal.")
        
        if not files or all(uploaded_file.filename == "" for uploaded_file in files):
            return _upload_error("Please select at least one file.")

        if not document_number:
            return _upload_error("Document number is required.")
        if not revision_number:
            revision_number = 'Rev.00'
        if not category:
            return _upload_error("Please select a Document Library category.")
        library_subcategory = (
            request.form.get('library_subcategory_hidden', '')
            or request.form.get('library_subcategory', '')
            or request.form.get('library_subcategory_select', '')
        ).strip()
        if not library_subcategory:
            return _upload_error("Please select the exact Document Library folder path before uploading.")
        if category == "qms" and ":" not in library_subcategory:
            library_subcategory = f"{AuthService.get_qms_level()}:{library_subcategory}"

        uploaded_count = 0
        email_failures = []

        saved_files = []
        for uploaded_file in files:
            if not uploaded_file or not uploaded_file.filename:
                continue

            record, error = DocumentService.save_upload(
                uploaded_file,
                session["user_name"],
                session["user_id"],
                session["user_email"],
                plant,
                department,
                customer,
                current_app.config["UPLOAD_FOLDER"],
                document_number,
                revision_number,
                category,
            )
            if error:
                email_failures.append(f"{uploaded_file.filename} (save failed: {error})")
                continue

            try:
                CategoryDocumentService.save_category_document(
                    category=library_category,
                    plant=plant,
                    department=department,
                    file_name=record['file_name'],
                    uploaded_by=session['user_name'],
                    user_id=session['user_id'],
                    sub_category=library_subcategory,
                    revision_number=revision_number,
                )
            except Exception as e:
                # Non-fatal: continue but notify
                email_failures.append(f"{record['file_name']} (library save failed: {str(e)})")
            else:
                saved_files.append(record['file_name'])

            uploaded_count += 1
            SystemLogService.log_upload(
                session["user_email"],
                session["user_name"],
                record["file_name"],
                plant,
                department,
            )

            NotificationService.create_notification(
                session["user_email"],
                "Upload submitted",
                f'{record.get("original_file_name", record["file_name"])} is pending approval.',
                link_url=url_for("dashboard.view_document", doc_id=record["id"]),
                notification_type="info",
            )

            sent_confirm, confirm_error = MailService.send_upload_confirmation(
                session["user_email"],
                record["file_name"],
                session["user_name"]
            )
            if not sent_confirm:
                email_failures.append(f"{record['file_name']} (upload confirmation failed: {confirm_error})")

            token = DocumentService.generate_review_token(
                record["id"],
                current_app.config["SECRET_KEY"],
                current_app.config["REVIEW_TOKEN_SALT"],
            )
            review_url = url_for("approvals.review_document", token=token, _external=True)
            first_approvers = UserStoreService.get_users_by_qms_level("L2")
            first_approver_emails = [user.get("email") for user in first_approvers if user.get("email")]
            if not first_approver_emails and current_app.config["APPROVAL_RECIPIENT"]:
                first_approver_emails = [current_app.config["APPROVAL_RECIPIENT"]]
            sent, mail_error = MailService.send_document_approval_request(
                first_approver_emails,
                review_url,
                record,
            )
            NotificationService.notify_qms_level(
                "L2",
                "First approval required",
                f'{record.get("original_file_name", record["file_name"])} from {record["department"]} is pending first approval.',
                link_url=url_for("approvals.review_document", token=token),
                notification_type="warning",
            )
            if sent:
                for recipient in first_approver_emails:
                    SystemLogService.log_approval_email(recipient, record["file_name"])
            else:
                email_failures.append(f"{record['file_name']} (approval request email failed: {mail_error})")

        if uploaded_count:
            flash(
                f"{uploaded_count} file(s) uploaded and moved to approvals as Pending.",
                "success",
            )
        else:
            flash("No files were uploaded.", "error")

        if email_failures:
            flash(
                "Approval email could not be sent for: " + ", ".join(email_failures),
                "warning",
            )

        # Return library redirect on success so the user can continue working with the selected category.
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'ok': True,
                'saved_files': saved_files,
                'email_failures': email_failures,
                'redirect': url_for('document_library.index', category_key=library_category) if library_category else url_for('document_library.index'),
            })

        if library_category:
            return redirect(url_for('document_library.index', category_key=library_category))

        return redirect(url_for("document_library.index"))

    # Pass document library categories and data for optional library uploads
    categories = DocumentLibraryService.get_categories()
    # Build a mapping of category_key -> data for the client to use when selecting subcategories
    library_data = {
        category['key']: DocumentLibraryService.get_client_category_data(
            category['key'],
            qms_level=AuthService.get_qms_level(),
            access_department=AuthService.get_visible_department(),
        )
        for category in categories
    }

    return render_template(
        "upload.html",
        customers=CUSTOMERS,
        current_user=current_user,
        library_categories=categories,
        library_data=library_data,
        PLANTS=PLANTS,
        DEPARTMENTS=DEPARTMENTS,
    )


@upload_bp.route("/document/<int:doc_id>/update", methods=["POST"])
def update_document(doc_id):
    """Admin-only: upload a new version of an existing document."""
    redir = _require_login()
    if redir:
        return redir

    current_user = AuthService.get_current_user()
    if not current_user or current_user.get('role') != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403

    file = request.files.get('file')
    if not file or not file.filename:
        flash("Please select a file to upload.", "error")
        return redirect(url_for('dashboard.index'))

    revision_number = request.form.get('revision_number', '').strip()
    if not revision_number:
        flash("Revision number is required for document updates.", "error")
        return redirect(url_for('dashboard.index'))

    change_summary = request.form.get('change_summary', '').strip()

    updated_doc, error = DocumentService.save_updated_version(
        doc_id, file,
        session['user_name'], session['user_id'], session['user_email'],
        current_app.config['UPLOAD_FOLDER'],
        revision_number,
        change_summary
    )
    if error:
        flash(f"Update failed: {error}", "error")
        return redirect(url_for('dashboard.index'))

    SystemLogService.log_upload(
        session['user_email'], session['user_name'],
        updated_doc['file_name'], updated_doc['plant'], updated_doc['department']
    )

    RevisionHistoryService.add_revision(
        document_id=updated_doc.get("id"),
        file_name=updated_doc["file_name"],
        revision_number=revision_number,
        revised_by=session["user_name"],
        user_id=session["user_id"],
        plant=updated_doc.get("plant"),
        department=updated_doc.get("department"),
        change_summary=change_summary,
        previous_file_name=updated_doc.get("previous_file_name"),
    )

    # Send approval email for new version
    token = DocumentService.generate_review_token(
        updated_doc['id'],
        current_app.config['SECRET_KEY'],
        current_app.config['REVIEW_TOKEN_SALT'],
    )
    review_url = url_for('approvals.review_document', token=token, _external=True)
    first_approvers = UserStoreService.get_users_by_qms_level("L2")
    first_approver_emails = [user.get("email") for user in first_approvers if user.get("email")]
    if not first_approver_emails and current_app.config["APPROVAL_RECIPIENT"]:
        first_approver_emails = [current_app.config["APPROVAL_RECIPIENT"]]
    MailService.send_document_approval_request(
        first_approver_emails,
        review_url,
        updated_doc,
    )
    NotificationService.notify_qms_level(
        "L2",
        "Updated document pending first approval",
        f'{updated_doc.get("original_file_name", updated_doc["file_name"])} is awaiting first approval.',
        link_url=url_for("approvals.review_document", token=token),
        notification_type="warning",
    )

    flash(f"Document updated to version {updated_doc.get('current_version', '')}. Sent for approval.", "success")
    return redirect(url_for('dashboard.index'))
