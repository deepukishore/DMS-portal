import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-dms-secret-key-change-in-production')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    USER_DB_PATH = os.path.join(BASE_DIR, 'data', 'smart_dms_users.sqlite3')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'deepu004.dk@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'sjhd dofp hzof qpou')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'deepu004.dk@gmail.com')

    APPROVAL_RECIPIENT = os.environ.get('APPROVAL_RECIPIENT', 'anithaashok2000@gmail.com')
    REVIEW_TOKEN_SALT = os.environ.get('REVIEW_TOKEN_SALT', 'smart-dms-approval-review')
