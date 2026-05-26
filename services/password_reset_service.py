from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from services.user_store_service import UserStoreService

_serializer = None


class PasswordResetService:
    """Generates and validates secure password reset tokens."""

    @staticmethod
    def init_app(app):
        global _serializer
        _serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    @staticmethod
    def generate_token(email):
        return _serializer.dumps(email, salt='password-reset')

    @staticmethod
    def verify_token(token, max_age=3600):
        try:
            email = _serializer.loads(token, salt='password-reset', max_age=max_age)
            return email, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def reset_password(email, new_password):
        if not UserStoreService.email_exists(email):
            return False, 'User not found.'
        updated = UserStoreService.update_password(email, generate_password_hash(new_password))
        if not updated:
            return False, 'User not found.'
        return True, None
