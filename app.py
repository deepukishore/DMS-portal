import os
from flask import Flask
from config import Config
from extensions import mail
from database import init_db
from services.auth_service import AuthService
from services.password_reset_service import PasswordResetService
from services.user_store_service import UserStoreService
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.upload_routes import upload_bp
from routes.approval_routes import approval_bp
from routes.tracking_routes import tracking_bp
from routes.archive_routes import archive_bp
from routes.document_library_routes import document_library_bp
from routes.plant_assets_routes import plant_assets_bp
from routes.customer_records_routes import customer_records_bp
from routes.procedures_routes import procedures_bp
from routes.category_routes import category_bp
from routes.system_log_routes import system_log_bp
from routes.profile_routes import profile_bp
from routes.graphics_report_routes import graphics_report_bp
from routes.revision_history_routes import revision_history_bp
from routes.about_routes import about_bp
from routes.notification_routes import notification_bp
from routes.people_routes import people_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()

    mail.init_app(app)
    PasswordResetService.init_app(app)
    UserStoreService.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(archive_bp)
    app.register_blueprint(document_library_bp)
    app.register_blueprint(plant_assets_bp)
    app.register_blueprint(customer_records_bp)
    app.register_blueprint(procedures_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(system_log_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(graphics_report_bp)
    app.register_blueprint(revision_history_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(people_bp)

    # Expose Python builtins needed in templates
    app.jinja_env.globals.update(zip=zip)

    @app.context_processor
    def inject_user_context():
        from services.document_service import DocumentService
        from services.notification_service import NotificationService
        current_user = AuthService.get_current_user()
        visible_department = AuthService.get_visible_department(current_user)
        try:
            all_docs = DocumentService.get_all_documents(access_department=visible_department)
            pending_count = sum(1 for d in all_docs if d.get('approval_status') == 'Pending')
        except Exception:
            pending_count = 0
        user_email = (current_user or {}).get("email", "")
        try:
            notifications = NotificationService.get_recent_for_user(user_email) if user_email else []
            notification_unread_count = NotificationService.get_unread_count(user_email) if user_email else 0
        except Exception:
            notifications = []
            notification_unread_count = 0
        return {
            "current_user": current_user,
            "can_access_admin_sections": AuthService.has_high_level_access(current_user),
            "is_admin_user": AuthService.is_admin(current_user),
            "pending_count": pending_count,
            "notifications": notifications,
            "notification_unread_count": notification_unread_count,
        }

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
