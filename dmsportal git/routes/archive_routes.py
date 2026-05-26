from flask import Blueprint, flash, redirect, render_template, session, url_for
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.system_log_service import SystemLogService

archive_bp = Blueprint('archive', __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return None


def _require_high_level_access():
    if not AuthService.has_high_level_access():
        flash("Archive access is limited to admins and higher-level users.", "error")
        return redirect(url_for("dashboard.index"))
    return None


@archive_bp.route('/archive')
def index():
    redir = _require_login()
    if redir:
        return redir
    access_redir = _require_high_level_access()
    if access_redir:
        return access_redir
    
    archived_records = DocumentService.get_all_archived_records()
    return render_template('archive.html', records=archived_records)


@archive_bp.route('/archive/delete/<int:archive_index>', methods=['POST'])
def delete_archived(archive_index):
    redir = _require_login()
    if redir:
        return redir
    access_redir = _require_high_level_access()
    if access_redir:
        return access_redir
    
    deleted, error = DocumentService.delete_archived_record(archive_index)
    
    if deleted:
        # Log the permanent deletion but keep the archive log
        SystemLogService.log_delete(
            session["user_email"],
            session["user_name"],
            deleted["file_name"],
            deleted["plant"],
            deleted["department"],
        )
        flash(f'"{deleted["file_name"]}" permanently deleted from archive.', "success")
    else:
        flash(error, "error")
    
    return redirect(url_for("archive.index"))
