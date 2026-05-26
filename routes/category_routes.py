from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from data.mock_data import DEPARTMENTS
from services.auth_service import AuthService
from services.category_document_service import CategoryDocumentService
from services.system_log_service import SystemLogService
from data.mock_data import MASTER_RECORD_PLANTS

category_bp = Blueprint('categories', __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return None


CATEGORIES_CONFIG = {
    'std-manual': {
        'key': 'std_manual',
        'label': 'Standard Manual',
        'title': 'Standard Manual',
    },
    'awards': {
        'key': 'awards',
        'label': 'Awards',
        'title': 'Awards',
    },
    'certification': {
        'key': 'certification',
        'label': 'Certification',
        'title': 'Certification',
    },
    'cq-manuals': {
        'key': 'cq_manuals',
        'label': 'CQ Manuals',
        'title': 'CQ Manuals',
    },
    'business-procedures': {
        'key': 'business_procedures',
        'label': 'Business Procedures',
        'title': 'Business Procedures',
    },
    'core-tool-manuals': {
        'key': 'core_tool_manuals',
        'label': 'Core Tool Manuals',
        'title': 'Core Tool Manuals',
    },
}


@category_bp.route('/std-manual')
def std_manual():
    redir = _require_login()
    if redir:
        return redir
    config = CATEGORIES_CONFIG['std-manual']
    plants = MASTER_RECORD_PLANTS
    preselect_plant = request.args.get('plant', '')
    preselect_dept = request.args.get('dept', '')
    return render_template('category_browser.html',
                          category_title=config['title'],
                          category_key=config['key'],
                          category_slug='std-manual',
                          plants=plants,
                          preselect_plant=preselect_plant,
                          preselect_dept=preselect_dept)


@category_bp.route('/awards')
def awards():
    redir = _require_login()
    if redir:
        return redir
    config = CATEGORIES_CONFIG['awards']
    plants = MASTER_RECORD_PLANTS
    preselect_plant = request.args.get('plant', '')
    preselect_dept = request.args.get('dept', '')
    return render_template('category_browser.html',
                          category_title=config['title'],
                          category_key=config['key'],
                          category_slug='awards',
                          plants=plants,
                          preselect_plant=preselect_plant,
                          preselect_dept=preselect_dept)


@category_bp.route('/certification')
def certification():
    redir = _require_login()
    if redir:
        return redir
    config = CATEGORIES_CONFIG['certification']
    plants = MASTER_RECORD_PLANTS
    preselect_plant = request.args.get('plant', '')
    preselect_dept = request.args.get('dept', '')
    return render_template('category_browser.html',
                          category_title=config['title'],
                          category_key=config['key'],
                          category_slug='certification',
                          plants=plants,
                          preselect_plant=preselect_plant,
                          preselect_dept=preselect_dept)


@category_bp.route('/cq-manuals')
def cq_manuals():
    redir = _require_login()
    if redir:
        return redir
    config = CATEGORIES_CONFIG['cq-manuals']
    plants = MASTER_RECORD_PLANTS
    preselect_plant = request.args.get('plant', '')
    preselect_dept = request.args.get('dept', '')
    return render_template('category_browser.html',
                          category_title=config['title'],
                          category_key=config['key'],
                          category_slug='cq-manuals',
                          plants=plants,
                          preselect_plant=preselect_plant,
                          preselect_dept=preselect_dept)


@category_bp.route('/business-procedures')
def business_procedures():
    redir = _require_login()
    if redir:
        return redir
    config = CATEGORIES_CONFIG['business-procedures']
    plants = MASTER_RECORD_PLANTS
    preselect_plant = request.args.get('plant', '')
    preselect_dept = request.args.get('dept', '')
    return render_template('category_browser.html',
                          category_title=config['title'],
                          category_key=config['key'],
                          category_slug='business-procedures',
                          plants=plants,
                          preselect_plant=preselect_plant,
                          preselect_dept=preselect_dept)


@category_bp.route('/core-tool-manuals')
def core_tool_manuals():
    redir = _require_login()
    if redir:
        return redir
    config = CATEGORIES_CONFIG['core-tool-manuals']
    plants = MASTER_RECORD_PLANTS
    preselect_plant = request.args.get('plant', '')
    preselect_dept = request.args.get('dept', '')
    return render_template('category_browser.html',
                          category_title=config['title'],
                          category_key=config['key'],
                          category_slug='core-tool-manuals',
                          plants=plants,
                          preselect_plant=preselect_plant,
                          preselect_dept=preselect_dept)


@category_bp.route('/categories/departments', methods=['GET'])
def get_departments():
    """Get departments for a plant (AJAX endpoint)."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({'departments': list(DEPARTMENTS)})


@category_bp.route('/categories/files', methods=['GET'])
def get_files():
    """Get files for a plant/department combination (AJAX endpoint)."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    
    plant_label = request.args.get('plant', '')
    department = request.args.get('department', '')
    category = request.args.get('category', '')
    
    files = CategoryDocumentService.get_files_for_category(
        category=category,
        plant=plant_label,
        department=department
    )
    
    return jsonify({'files': files})


@category_bp.route('/categories/view', methods=['POST'])
def view_file():
    """Log file view (AJAX endpoint)."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    file_name = data.get('file_name', '')
    plant = data.get('plant', '')
    department = data.get('department', '')
    category = data.get('category', '')
    
    SystemLogService.log_view(
        session['user_email'], session['user_name'],
        file_name, f'{category} — {plant} / {department}'
    )
    
    return jsonify({'ok': True})
