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

    import math
    action_filter = request.args.get('action', '')
    page = max(1, request.args.get('page', 1, type=int))
    page_size = request.args.get('page_size', 10, type=int)
    if page_size not in (10, 25, 50, 100):
        page_size = 10

    logs = SystemLogService.get_logs_by_action(action_filter) if action_filter else SystemLogService.get_all_logs()
    total = len(logs)
    page_count = max(1, math.ceil(total / page_size))
    page = min(page, page_count)
    page_logs = logs[(page - 1) * page_size: page * page_size]

    return render_template('system_log.html',
        logs=page_logs,
        total_logs=total,
        action_filter=action_filter,
        page=page,
        page_size=page_size,
        page_count=page_count,
    )
