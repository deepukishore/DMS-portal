from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from data.departments import OFFICIAL_DEPARTMENTS, normalize_department
from services.user_store_service import UserStoreService


class AuthService:
    """Handles user authentication: login, logout, registration."""

    HIGH_LEVEL_ROLES = {"Admin", "Manager", "Supervisor", "Approver"}

    @staticmethod
    def _set_session(user):
        """Write all user fields into the Flask session."""
        role = user.get('role', 'User')
        # Admin always has full L1 access regardless of stored level
        qms_level = 'L1' if role == 'Admin' else user.get('qms_level', 'L4')
        session['user_email']      = user['email']
        session['user_name']       = user['name']
        session['user_id']         = user['user_id']
        session['user_emp_id']     = user.get('emp_id', '')
        session['user_mobile']     = user.get('mobile', '')
        session['user_plant']      = user.get('plant', '')
        session['user_department'] = user.get('department', '')
        session['user_role']       = role
        session['user_qms_level']  = qms_level

    @staticmethod
    def login(email, password):
        user = UserStoreService.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            AuthService._set_session(user)
            return user, None
        return None, 'Invalid email or password.'

    @staticmethod
    def login_by_genid(genid, password):
        user = UserStoreService.get_user_by_genid(genid)
        if user and check_password_hash(user['password_hash'], password):
            AuthService._set_session(user)
            return user, None
        return None, 'Invalid GENID or password.'

    @staticmethod
    def logout():
        session.clear()

    @staticmethod
    def register(name, email, password, emp_id='', plant='', department=''):
        department = normalize_department(department)
        if UserStoreService.email_exists(email):
            return None, 'An account with this email already exists.'
        if len(password) < 8:
            return None, 'Password must be at least 8 characters.'
        if not plant or not department:
            return None, 'Plant and department are required.'
        if department not in OFFICIAL_DEPARTMENTS:
            return None, 'Please choose one of the official departments.'
        user = UserStoreService.create_user(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            emp_id=emp_id,
            plant=plant,
            department=department,
            role='User',
        )
        return user, None

    @staticmethod
    def get_current_user():
        email = session.get('user_email')
        if email:
            return UserStoreService.get_user_by_email(email)
        return None

    @staticmethod
    def is_logged_in():
        return 'user_email' in session

    @staticmethod
    def has_high_level_access(user=None):
        if user is None:
            user = AuthService.get_current_user()
        if not user:
            return False
        return user.get('role', 'User') in AuthService.HIGH_LEVEL_ROLES

    @staticmethod
    def is_admin(user=None):
        if user is None:
            user = AuthService.get_current_user()
        if not user:
            return False
        return user.get('role', 'User') == 'Admin'

    @staticmethod
    def get_qms_level():
        """Return the current user's QMS access level (L1–L4). Admin always L1."""
        return session.get('user_qms_level', 'L4')

    @staticmethod
    def is_qms_first_approver(user=None):
        if user is None:
            user = AuthService.get_current_user()
        if not user:
            return False
        return user.get("qms_level") == "L2"

    @staticmethod
    def is_qms_final_approver(user=None):
        if user is None:
            user = AuthService.get_current_user()
        if not user:
            return False
        return user.get("qms_level") == "L1" or user.get("role") == "Admin"

    @staticmethod
    def get_visible_department(user=None):
        return ""
