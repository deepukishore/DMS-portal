from pathlib import Path

from flask import Blueprint, jsonify, redirect, render_template, request, send_file, session, url_for

from services.auth_service import AuthService
from services.document_library_service import DocumentLibraryService
from services.plant_asset_service import PlantAssetService
from services.system_log_service import SystemLogService

document_library_bp = Blueprint("document_library", __name__)

IATF_AUDIT_NC_CAPA_TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "download_templates"
    / "IATF 16949 -2016 2nd Surveillance  Audit NCs Tracking Report - Format.xlsx"
)


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
    categories = DocumentLibraryService.get_categories()

    # The root URL is a true library landing page. Category links below use
    # normal anchors, so opening a folder loads its own dedicated page instead
    # of swapping content inside the landing page.
    if category_key is None:
        return render_template(
            "document_library.html",
            is_overview=True,
            categories=DocumentLibraryService.get_dashboard_statistics(
                qms_level=AuthService.get_qms_level(),
                access_department=access_department,
            ),
        )

    resolved_key, default_primary, default_secondary = (
        DocumentLibraryService.resolve_category(category_key)
    )
    preselected_primary = request.args.get("primary", default_primary)
    preselected_secondary = request.args.get("secondary", default_secondary)
    preselected_tertiary = request.args.get("tertiary", "")
    preselected_plant = request.args.get("plant", "")
    preselected_department = request.args.get("department", "")
    active_category = next(
        (category for category in categories if category["key"] == resolved_key),
        categories[0],
    )

    return render_template(
        "document_library.html",
        is_overview=False,
        categories=categories,
        active_category=active_category,
        category_key=resolved_key,
        category_data=DocumentLibraryService.get_client_category_data(
            resolved_key,
            qms_level=AuthService.get_qms_level(),
            access_department=access_department,
        ),
        preselected_primary=preselected_primary,
        preselected_secondary=preselected_secondary,
        preselected_tertiary=preselected_tertiary,
        preselected_plant=preselected_plant,
        preselected_department=preselected_department,
    )


@document_library_bp.route("/document-library/iatf-audit-nc-capa-format")
def download_iatf_audit_nc_capa_format():
    redir = _require_login()
    if redir:
        return redir

    return send_file(
        IATF_AUDIT_NC_CAPA_TEMPLATE,
        as_attachment=True,
        download_name=IATF_AUDIT_NC_CAPA_TEMPLATE.name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
