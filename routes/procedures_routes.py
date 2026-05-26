from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from data.mock_data import DEPARTMENTS
from services.auth_service import AuthService
from services.category_document_service import CategoryDocumentService
from services.system_log_service import SystemLogService
from data.mock_data import MASTER_RECORD_PLANTS

procedures_bp = Blueprint('procedures', __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return None


PROCEDURE_SUBCATEGORIES = {
    'management': {
        'key': 'management_oriented',
        'label': 'Management Oriented Procedures',
        'description': 'Management-level procedures and guidelines',
    },
    'customer': {
        'key': 'customer_oriented',
        'label': 'Customer Oriented Procedures',
        'description': 'Customer-facing procedures and processes',
    },
    'support': {
        'key': 'support_oriented',
        'label': 'Support Oriented Procedures',
        'description': 'Support and maintenance procedures',
    },
    'plant': {
        'key': 'plant_procedures',
        'label': 'Plant Procedures',
        'description': 'Procedures related to all four plants',
    },
}


@procedures_bp.route('/procedures')
def index():
    """Show procedures sub-category selection page."""
    redir = _require_login()
    if redir:
        return redir
    
    categories = [
        {
            'key': 'management',
            'label': 'Management Oriented',
            'icon': '📋',
            'description': 'Management-level procedures and guidelines',
        },
        {
            'key': 'customer',
            'label': 'Customer Oriented',
            'icon': '🤝',
            'description': 'Customer-facing procedures and processes',
        },
        {
            'key': 'support',
            'label': 'Support Oriented',
            'icon': '🔧',
            'description': 'Support and maintenance procedures',
        },
        {
            'key': 'plant',
            'label': 'Plant Procedures',
            'icon': '🏭',
            'description': 'Procedures related to all four plants',
        },
    ]
    
    return render_template('procedures.html', categories=categories)


@procedures_bp.route('/procedures/<sub_category>')
def sub_index(sub_category):
    """Show procedures browser for a specific sub-category."""
    redir = _require_login()
    if redir:
        return redir
    
    if sub_category not in PROCEDURE_SUBCATEGORIES:
        return redirect(url_for('procedures.index'))
    
    sub_cat_info = PROCEDURE_SUBCATEGORIES[sub_category]
    plants = MASTER_RECORD_PLANTS
    
    return render_template('procedures_browser.html', 
                          category_title=sub_cat_info['label'],
                          category_key=sub_cat_info['key'],
                          sub_category_key=sub_category,
                          plants=plants)


@procedures_bp.route('/procedures/departments', methods=['GET'])
def get_departments():
    """Get departments for a plant (AJAX endpoint)."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({'departments': list(DEPARTMENTS)})


@procedures_bp.route('/procedures/files', methods=['GET'])
def get_files():
    """Get files for a plant/department combination (AJAX endpoint)."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    
    plant_label = request.args.get('plant', '')
    department = request.args.get('department', '')
    sub_category = request.args.get('sub_category', '')
    
    files = CategoryDocumentService.get_files_for_category(
        category='procedures',
        plant=plant_label,
        department=department,
        sub_category=sub_category
    )
    
    return jsonify({'files': files})


@procedures_bp.route('/procedures/view', methods=['POST'])
def view_file():
    """Log file view (AJAX endpoint)."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    file_name = data.get('file_name', '')
    plant = data.get('plant', '')
    department = data.get('department', '')
    sub_category = data.get('sub_category', '')
    
    sub_cat_info = PROCEDURE_SUBCATEGORIES.get(sub_category, {})
    sub_label = sub_cat_info.get('label', sub_category)
    
    SystemLogService.log_view(
        session['user_email'], session['user_name'],
        file_name, f'Procedures — {sub_label} / {plant} / {department}'
    )
    
    return jsonify({'ok': True})
