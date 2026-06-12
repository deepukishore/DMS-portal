from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from services.auth_service import AuthService
from services.document_library_service import DocumentLibraryService
from services.plant_asset_service import PlantAssetService
from services.system_log_service import SystemLogService

document_library_bp = Blueprint("document_library", __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for("auth.login"))
    return None


@document_library_bp.route("/document-library")
@document_library_bp.route("/document-library/<category_key>")
def index(category_key=None):
    redir = _require_login()
    if redir:
        return redir

    access_department = AuthService.get_visible_department()
    resolved_key, default_primary, default_secondary = (
        DocumentLibraryService.resolve_category(category_key)
    )
    preselected_primary = request.args.get("primary", default_primary)
    preselected_secondary = request.args.get("secondary", default_secondary)
    categories = DocumentLibraryService.get_categories()
    active_category = next(
        (category for category in categories if category["key"] == resolved_key),
        categories[0],
    )

    return render_template(
        "document_library.html",
        categories=categories,
        active_category=active_category,
        category_key=resolved_key,
        category_data=DocumentLibraryService.get_category_data(resolved_key, access_department=access_department),
        preselected_primary=preselected_primary,
        preselected_secondary=preselected_secondary,
        user_qms_level=AuthService.get_qms_level(),
        is_admin=AuthService.is_admin(),
    )


@document_library_bp.route("/document-library/view", methods=["POST"])
def view_file():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    SystemLogService.log_view(
        session["user_email"],
        session["user_name"],
        data.get("file_name", ""),
        f"Document Library - {data.get('category', '')}",
    )
    return jsonify({"ok": True})


@document_library_bp.route("/document-library/master-records/departments")
def master_record_departments():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Unauthorized"}), 401

    plant_label = request.args.get("plant", "")
    departments = PlantAssetService.get_departments_for_plant(
        plant_label,
        access_department=AuthService.get_visible_department(),
    )
    return jsonify({"departments": departments})


@document_library_bp.route("/document-library/master-records/files")
def master_record_files():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Unauthorized"}), 401

    plant_label = request.args.get("plant", "")
    department = request.args.get("department", "")
    files = PlantAssetService.get_files_for_plant_department(
        plant_label,
        department,
        access_department=AuthService.get_visible_department(),
    )
    return jsonify({"files": files})
