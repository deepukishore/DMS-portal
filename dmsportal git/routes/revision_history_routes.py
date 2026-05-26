from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from services.auth_service import AuthService
from services.revision_history_service import RevisionHistoryService
from data.mock_data import MASTER_RECORD_PLANTS

revision_history_bp = Blueprint('revision_history', __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return None


@revision_history_bp.route('/revision-history')
def index():
    """Display revision history with filters."""
    redir = _require_login()
    if redir:
        return redir
    
    # Get filter parameters
    plant_filter = request.args.get('plant', '')
    department_filter = request.args.get('department', '')
    visible_department = AuthService.get_visible_department()
    effective_department = visible_department or department_filter
    
    # Get all revisions with optional filters
    revisions = RevisionHistoryService.get_all_revisions(
        plant=plant_filter if plant_filter else None,
        department=effective_department if effective_department else None
    )
    
    # Extract unique plants and departments from revision history
    plants_in_history = set()
    departments_in_history = set()
    
    for rev in revisions:
        if rev.get('plant'):
            plants_in_history.add(rev['plant'])
        if rev.get('department'):
            departments_in_history.add(rev['department'])
    
    # Combine with master records plants
    all_plants = MASTER_RECORD_PLANTS + [
        {'id': p, 'label': p, 'location': ''} 
        for p in plants_in_history 
        if p not in [x['label'] for x in MASTER_RECORD_PLANTS]
    ]
    
    return render_template('revision_history.html',
                          revisions=revisions,
                          plants=all_plants,
                          departments=sorted(list(departments_in_history)),
                          plant_filter=plant_filter,
                          department_filter=effective_department)


@revision_history_bp.route('/revision-history/add', methods=['POST'])
def add_revision():
    """Add a new revision entry."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    
    file_name = request.form.get('file_name', '').strip()
    revision_number = request.form.get('revision_number', 'Rev.00').strip()
    change_summary = request.form.get('change_summary', '').strip()
    plant = request.form.get('plant', '').strip()
    department = request.form.get('department', '').strip()
    previous_file_name = request.form.get('previous_file_name', '').strip()
    document_id = request.form.get('document_id', type=int)
    
    if not file_name:
        return jsonify({'error': 'File name is required'}), 400
    
    try:
        rev_id = RevisionHistoryService.add_revision(
            file_name=file_name,
            revision_number=revision_number,
            revised_by=session.get('user_name', 'Unknown'),
            user_id=session.get('user_id', ''),
            plant=plant if plant else None,
            department=department if department else None,
            change_summary=change_summary if change_summary else None,
            previous_file_name=previous_file_name if previous_file_name else None,
            document_id=document_id
        )
        
        return jsonify({
            'ok': True,
            'revision_id': rev_id,
            'message': f'Revision {revision_number} recorded successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@revision_history_bp.route('/revision-history/document/<file_name>')
def get_revisions_for_document(file_name):
    """Get all revisions for a specific document."""
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    
    revisions = RevisionHistoryService.get_revisions_for_document(file_name)
    return jsonify({
        'file_name': file_name,
        'revisions': revisions,
        'count': len(revisions)
    })
