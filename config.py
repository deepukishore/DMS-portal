import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-dms-secret-key-change-in-production')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    USER_DB_PATH = os.path.join(BASE_DIR, 'data', 'smart_dms_users.sqlite3')
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'smart_dms.db')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # Use DATABASE_ENGINE=mysql after setting the MySQL credentials below.
    # SQLite remains available as a local fallback and as the migration source.
    DATABASE_ENGINE = os.environ.get('DATABASE_ENGINE', 'sqlite').strip().lower()
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'smart_dms')
    MYSQL_CHARSET = os.environ.get('MYSQL_CHARSET', 'utf8mb4')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'deepu004.dk@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'sjhd dofp hzof qpou')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'deepu004.dk@gmail.com')

    FIRST_APPROVAL_RECIPIENT = os.environ.get(
        'FIRST_APPROVAL_RECIPIENT',
        'anithaashok2000@gmail.com',
    )
    FINAL_APPROVAL_RECIPIENT = os.environ.get(
        'FINAL_APPROVAL_RECIPIENT',
        'chefashokanna@gmail.com',
    )
    # Retained for compatibility with code that uses the original setting as a
    # generic approval-email fallback.
    APPROVAL_RECIPIENT = FIRST_APPROVAL_RECIPIENT
    REVIEW_TOKEN_SALT = os.environ.get('REVIEW_TOKEN_SALT', 'smart-dms-approval-review')
