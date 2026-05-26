from flask import Blueprint, flash, redirect, render_template, request, url_for
from services.auth_service import AuthService
from services.system_log_service import SystemLogService

system_log_bp = Blueprint('system_log', __name__)


@system_log_bp.route('/system-log')
def index():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    if not AuthService.has_high_level_access():
        flash("System log access is limited to admins and higher-level users.", "error")
        return redirect(url_for("dashboard.index"))
    action_filter = request.args.get('action', '')
    if action_filter:
        logs = SystemLogService.get_logs_by_action(action_filter)
    else:
        logs = SystemLogService.get_all_logs()
    return render_template('system_log.html', logs=logs, action_filter=action_filter)
