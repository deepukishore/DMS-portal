from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from services.auth_service import AuthService
from services.plant_asset_service import PlantAssetService
from services.system_log_service import SystemLogService

plant_assets_bp = Blueprint('plant_assets', __name__)


def _require_login():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return None


@plant_assets_bp.route('/plant-assets')
def index():
    redir = _require_login()
    if redir:
        return redir
    plants = PlantAssetService.get_all_plants()
    return render_template('plant_assets.html', plants=plants)


@plant_assets_bp.route('/plant-assets/departments')
def get_departments():
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    plant_label = request.args.get('plant', '')
    departments = PlantAssetService.get_departments_for_plant(plant_label, access_department=AuthService.get_visible_department())
    return jsonify({'departments': departments})


@plant_assets_bp.route('/plant-assets/files')
def get_files():
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    plant_label = request.args.get('plant', '')
    department = request.args.get('department', '')
    files = PlantAssetService.get_files_for_plant_department(plant_label, department, access_department=AuthService.get_visible_department())
    return jsonify({'files': files})


@plant_assets_bp.route('/plant-assets/view', methods=['POST'])
def view_file():
    redir = _require_login()
    if redir:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    file_name = data.get('file_name', '')
    plant = data.get('plant', '')
    department = data.get('department', '')
    SystemLogService.log_view(
        session['user_email'], session['user_name'],
        file_name, f'Plant Assets — {plant} / {department}'
    )
    return jsonify({'ok': True})
