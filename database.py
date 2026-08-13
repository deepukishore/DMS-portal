import os
import re
import sqlite3

from data.customers import LEGACY_CUSTOMER_MAP
from data.departments import LEGACY_DEPARTMENT_MAP
from data.document_categories import infer_document_category


_DATABASE_CONFIG = {
    "engine": os.environ.get("DATABASE_ENGINE", "sqlite").strip().lower(),
    "sqlite_path": os.path.abspath("smart_dms.db"),
    "mysql_host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "mysql_port": int(os.environ.get("MYSQL_PORT", 3306)),
    "mysql_user": os.environ.get("MYSQL_USER", "root"),
    "mysql_password": os.environ.get("MYSQL_PASSWORD", ""),
    "mysql_database": os.environ.get("MYSQL_DATABASE", "smart_dms"),
    "mysql_charset": os.environ.get("MYSQL_CHARSET", "utf8mb4"),
}


def configure_database(config):
    """Load database settings from the Flask configuration."""
    _DATABASE_CONFIG.update(
        {
            "engine": str(config.get("DATABASE_ENGINE", "sqlite")).strip().lower(),
            "sqlite_path": os.path.abspath(config.get("SQLITE_DB_PATH", "smart_dms.db")),
            "mysql_host": config.get("MYSQL_HOST", "127.0.0.1"),
            "mysql_port": int(config.get("MYSQL_PORT", 3306)),
            "mysql_user": config.get("MYSQL_USER", "root"),
            "mysql_password": config.get("MYSQL_PASSWORD", ""),
            "mysql_database": config.get("MYSQL_DATABASE", "smart_dms"),
            "mysql_charset": config.get("MYSQL_CHARSET", "utf8mb4"),
        }
    )
    if _DATABASE_CONFIG["engine"] not in {"sqlite", "mysql"}:
        raise ValueError("DATABASE_ENGINE must be either 'sqlite' or 'mysql'.")


def database_engine():
    return _DATABASE_CONFIG["engine"]


def is_mysql():
    return database_engine() == "mysql"


def _mysql_driver():
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError as exc:
        raise RuntimeError(
            "MySQL support requires PyMySQL. Install the project requirements first."
        ) from exc
    return pymysql, DictCursor


def _mysql_database_name():
    database_name = str(_DATABASE_CONFIG["mysql_database"]).strip()
    if not re.fullmatch(r"[A-Za-z0-9_]+", database_name):
        raise ValueError("MYSQL_DATABASE may contain only letters, numbers, and underscores.")
    return database_name


class _MySQLCursorAdapter:
    """Expose a SQLite-like cursor API while using PyMySQL underneath."""

    def __init__(self, cursor):
        self._cursor = cursor

    @staticmethod
    def _translate(query):
        return query.replace("?", "%s")

    def execute(self, query, params=None):
        translated = self._translate(query)
        normalized_params = tuple(params) if params else None
        self._cursor.execute(translated, normalized_params)
        return self

    def executemany(self, query, params):
        translated = self._translate(query)
        self._cursor.executemany(translated, params)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()

    def __iter__(self):
        return iter(self._cursor)


class _MySQLConnectionAdapter:
    """Connection wrapper used by existing services without backend-specific code."""

    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return _MySQLCursorAdapter(self._connection.cursor())

    def execute(self, query, params=None):
        return self.cursor().execute(query, params)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()
        return False


def _open_mysql_connection(include_database=True):
    pymysql, dict_cursor = _mysql_driver()
    connection_args = {
        "host": _DATABASE_CONFIG["mysql_host"],
        "port": _DATABASE_CONFIG["mysql_port"],
        "user": _DATABASE_CONFIG["mysql_user"],
        "password": _DATABASE_CONFIG["mysql_password"],
        "charset": _DATABASE_CONFIG["mysql_charset"],
        "cursorclass": dict_cursor,
        "autocommit": False,
        "connect_timeout": 8,
    }
    if include_database:
        connection_args["database"] = _mysql_database_name()
    return _MySQLConnectionAdapter(pymysql.connect(**connection_args))


def _ensure_mysql_database():
    database_name = _mysql_database_name()
    connection = _open_mysql_connection(include_database=False)
    try:
        cursor = connection.cursor()
        charset = _DATABASE_CONFIG["mysql_charset"]
        if not re.fullmatch(r"[A-Za-z0-9_]+", charset):
            raise ValueError("MYSQL_CHARSET contains unsupported characters.")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
            f"CHARACTER SET {charset} COLLATE {charset}_unicode_ci"
        )
        connection.commit()
    finally:
        connection.close()


def get_connection():
    if is_mysql():
        return _open_mysql_connection()

    connection = sqlite3.connect(_DATABASE_CONFIG["sqlite_path"])
    connection.row_factory = sqlite3.Row
    return connection


SQLITE_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        user_id TEXT NOT NULL UNIQUE,
        emp_id TEXT,
        plant TEXT,
        department TEXT,
        mobile TEXT,
        role TEXT NOT NULL DEFAULT 'User',
        password_hash TEXT NOT NULL,
        created_at TEXT,
        avatar TEXT,
        qms_level TEXT NOT NULL DEFAULT 'L4'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        user_id TEXT NOT NULL,
        uploader_email TEXT NOT NULL,
        plant TEXT NOT NULL,
        department TEXT NOT NULL,
        customer TEXT,
        file_name TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        approval_status TEXT DEFAULT 'Pending',
        approval_updated_at TEXT,
        pdf_file_name TEXT,
        original_file_name TEXT,
        current_version INTEGER DEFAULT 1,
        category TEXT,
        document_number TEXT,
        revision_number TEXT,
        rejection_comment TEXT,
        hold_comment TEXT,
        hold_by TEXT,
        held_at TEXT,
        resubmission_comment TEXT,
        resubmitted_at TEXT,
        decision_by TEXT,
        selected_recipients TEXT,
        first_approver TEXT,
        first_approved_at TEXT,
        final_approver TEXT,
        final_approved_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        link_url TEXT,
        notification_type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        file_name TEXT NOT NULL,
        plant TEXT NOT NULL,
        department TEXT NOT NULL,
        customer TEXT,
        uploaded_by TEXT,
        user_id TEXT,
        approval_status TEXT,
        original_upload_date TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_name TEXT NOT NULL,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS category_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        sub_category TEXT,
        plant TEXT NOT NULL,
        department TEXT NOT NULL,
        file_name TEXT NOT NULL,
        uploaded_by TEXT,
        user_id TEXT,
        uploaded_at TEXT,
        approval_status TEXT DEFAULT 'Pending',
        revision_number TEXT DEFAULT 'Rev.00'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS revision_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        file_name TEXT NOT NULL,
        revision_number TEXT NOT NULL,
        revised_by TEXT NOT NULL,
        user_id TEXT NOT NULL,
        plant TEXT,
        department TEXT,
        revision_date TEXT NOT NULL,
        change_summary TEXT,
        previous_file_name TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS document_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        version_number INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        original_file_name TEXT NOT NULL,
        pdf_file_name TEXT NOT NULL,
        uploaded_by TEXT NOT NULL,
        user_id TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        change_summary TEXT,
        document_number TEXT,
        revision_number TEXT,
        category TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS document_number_sequences (
        plant_code TEXT PRIMARY KEY,
        last_number INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS recently_viewed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        document_id INTEGER NOT NULL,
        viewed_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        document_id INTEGER NOT NULL,
        bookmarked_at TEXT NOT NULL,
        UNIQUE(user_email, document_id)
    )
    """,
]


MYSQL_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        email VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        user_id VARCHAR(64) NOT NULL UNIQUE,
        emp_id VARCHAR(64),
        plant VARCHAR(255),
        department VARCHAR(255),
        mobile VARCHAR(40),
        role VARCHAR(80) NOT NULL DEFAULT 'User',
        password_hash VARCHAR(512) NOT NULL,
        created_at VARCHAR(32),
        avatar VARCHAR(500),
        qms_level VARCHAR(8) NOT NULL DEFAULT 'L4'
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        user_id VARCHAR(64) NOT NULL,
        uploader_email VARCHAR(255) NOT NULL,
        plant VARCHAR(255) NOT NULL,
        department VARCHAR(255) NOT NULL,
        customer VARCHAR(255),
        file_name VARCHAR(500) NOT NULL,
        uploaded_at VARCHAR(32) NOT NULL,
        approval_status VARCHAR(80) DEFAULT 'Pending',
        approval_updated_at VARCHAR(32),
        pdf_file_name VARCHAR(500),
        original_file_name VARCHAR(500),
        current_version INT DEFAULT 1,
        category VARCHAR(255),
        document_number VARCHAR(255),
        revision_number VARCHAR(80),
        rejection_comment LONGTEXT,
        hold_comment LONGTEXT,
        hold_by VARCHAR(255),
        held_at VARCHAR(32),
        resubmission_comment LONGTEXT,
        resubmitted_at VARCHAR(32),
        decision_by VARCHAR(255),
        selected_recipients LONGTEXT,
        first_approver VARCHAR(255),
        first_approved_at VARCHAR(32),
        final_approver VARCHAR(255),
        final_approved_at VARCHAR(32)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        user_email VARCHAR(255) NOT NULL,
        title VARCHAR(255) NOT NULL,
        message LONGTEXT NOT NULL,
        link_url VARCHAR(1000),
        notification_type VARCHAR(80) DEFAULT 'info',
        is_read TINYINT(1) DEFAULT 0,
        created_at VARCHAR(32) NOT NULL,
        INDEX idx_notifications_user (user_email, is_read)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS archive (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        timestamp VARCHAR(32) NOT NULL,
        file_name VARCHAR(500) NOT NULL,
        plant VARCHAR(255) NOT NULL,
        department VARCHAR(255) NOT NULL,
        customer VARCHAR(255),
        uploaded_by VARCHAR(255),
        user_id VARCHAR(255),
        approval_status VARCHAR(80),
        original_upload_date VARCHAR(32)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS system_logs (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        timestamp VARCHAR(32) NOT NULL,
        user_name VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        action VARCHAR(80) NOT NULL,
        details LONGTEXT,
        INDEX idx_logs_user (user_id),
        INDEX idx_logs_action (action),
        INDEX idx_logs_timestamp (timestamp)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS category_documents (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        category VARCHAR(255) NOT NULL,
        sub_category VARCHAR(255),
        plant VARCHAR(255) NOT NULL,
        department VARCHAR(255) NOT NULL,
        file_name VARCHAR(500) NOT NULL,
        uploaded_by VARCHAR(255),
        user_id VARCHAR(255),
        uploaded_at VARCHAR(32),
        approval_status VARCHAR(80) DEFAULT 'Pending',
        revision_number VARCHAR(80) DEFAULT 'Rev.00'
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS revision_history (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        document_id BIGINT,
        file_name VARCHAR(500) NOT NULL,
        revision_number VARCHAR(80) NOT NULL,
        revised_by VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        plant VARCHAR(255),
        department VARCHAR(255),
        revision_date VARCHAR(32) NOT NULL,
        change_summary LONGTEXT,
        previous_file_name VARCHAR(500)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS document_versions (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        document_id BIGINT NOT NULL,
        version_number INT NOT NULL,
        file_name VARCHAR(500) NOT NULL,
        original_file_name VARCHAR(500) NOT NULL,
        pdf_file_name VARCHAR(500) NOT NULL,
        uploaded_by VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        uploaded_at VARCHAR(32) NOT NULL,
        change_summary LONGTEXT,
        document_number VARCHAR(255),
        revision_number VARCHAR(80),
        category VARCHAR(255),
        INDEX idx_versions_document (document_id, version_number)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS document_number_sequences (
        plant_code VARCHAR(8) PRIMARY KEY,
        last_number INT NOT NULL DEFAULT 0
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS recently_viewed (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        user_email VARCHAR(255) NOT NULL,
        document_id BIGINT NOT NULL,
        viewed_at VARCHAR(32) NOT NULL,
        INDEX idx_recent_user (user_email, viewed_at)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS bookmarks (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        user_email VARCHAR(255) NOT NULL,
        document_id BIGINT NOT NULL,
        bookmarked_at VARCHAR(32) NOT NULL,
        UNIQUE KEY uq_bookmark_user_document (user_email, document_id)
    ) ENGINE=InnoDB
    """,
]


REQUIRED_COLUMNS = {
    "users": {
        "mobile": ("TEXT", "VARCHAR(40)"),
        "avatar": ("TEXT", "VARCHAR(500)"),
        "qms_level": ("TEXT NOT NULL DEFAULT 'L4'", "VARCHAR(8) NOT NULL DEFAULT 'L4'"),
        "created_at": ("TEXT", "VARCHAR(32)"),
    },
    "documents": {
        "pdf_file_name": ("TEXT", "VARCHAR(500)"),
        "original_file_name": ("TEXT", "VARCHAR(500)"),
        "current_version": ("INTEGER DEFAULT 1", "INT DEFAULT 1"),
        "category": ("TEXT", "VARCHAR(255)"),
        "document_number": ("TEXT", "VARCHAR(255)"),
        "revision_number": ("TEXT", "VARCHAR(80)"),
        "rejection_comment": ("TEXT", "LONGTEXT"),
        "hold_comment": ("TEXT", "LONGTEXT"),
        "hold_by": ("TEXT", "VARCHAR(255)"),
        "held_at": ("TEXT", "VARCHAR(32)"),
        "resubmission_comment": ("TEXT", "LONGTEXT"),
        "resubmitted_at": ("TEXT", "VARCHAR(32)"),
        "decision_by": ("TEXT", "VARCHAR(255)"),
        "selected_recipients": ("TEXT", "LONGTEXT"),
        "first_approver": ("TEXT", "VARCHAR(255)"),
        "first_approved_at": ("TEXT", "VARCHAR(32)"),
        "final_approver": ("TEXT", "VARCHAR(255)"),
        "final_approved_at": ("TEXT", "VARCHAR(32)"),
    },
    "document_versions": {
        "document_number": ("TEXT", "VARCHAR(255)"),
        "revision_number": ("TEXT", "VARCHAR(80)"),
        "category": ("TEXT", "VARCHAR(255)"),
    },
}


def _column_exists(cursor, table_name, column_name):
    if is_mysql():
        cursor.execute(
            """
            SELECT 1 AS present
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ? AND column_name = ?
            LIMIT 1
            """,
            (_mysql_database_name(), table_name, column_name),
        )
        return cursor.fetchone() is not None

    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(row["name"] == column_name for row in cursor.fetchall())


def _ensure_required_columns(cursor):
    definition_index = 1 if is_mysql() else 0
    for table_name, columns in REQUIRED_COLUMNS.items():
        for column_name, definitions in columns.items():
            if not _column_exists(cursor, table_name, column_name):
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} "
                    f"{definitions[definition_index]}"
                )


def _migrate_departments(cursor):
    table_names = [
        "users",
        "documents",
        "archive",
        "revision_history",
        "category_documents",
    ]
    for old_value, new_value in LEGACY_DEPARTMENT_MAP.items():
        for table_name in table_names:
            cursor.execute(
                f"UPDATE {table_name} SET department = ? WHERE department = ?",
                (new_value, old_value),
            )
        log_replacements = [
            (f"({old_value},", f"({new_value},"),
            (f"to {old_value}", f"to {new_value}"),
            (f"/ {old_value}.", f"/ {new_value}."),
            (f"/ {old_value} /", f"/ {new_value} /"),
        ]
        for old_fragment, new_fragment in log_replacements:
            cursor.execute(
                "UPDATE system_logs SET details = REPLACE(details, ?, ?) WHERE details LIKE ?",
                (old_fragment, new_fragment, f"%{old_fragment}%"),
            )


def _migrate_customers(cursor):
    cursor.execute(
        "UPDATE documents SET customer = 'Internal' WHERE customer IS NULL OR customer = ''"
    )
    cursor.execute(
        "UPDATE archive SET customer = 'Internal' WHERE customer IS NULL OR customer = ''"
    )
    for old_value, new_value in LEGACY_CUSTOMER_MAP.items():
        if old_value == new_value or old_value == "Internal":
            continue
        cursor.execute(
            "UPDATE documents SET customer = ? WHERE customer = ?",
            (new_value, old_value),
        )
        cursor.execute(
            "UPDATE archive SET customer = ? WHERE customer = ?",
            (new_value, old_value),
        )


def _migrate_plants(cursor):
    """Correct the Guduvanchery spelling in existing persisted records."""
    table_names = [
        "users",
        "documents",
        "archive",
        "revision_history",
        "category_documents",
    ]
    replacements = {
        "P2 - Guduvachery Plant": "P2 - Guduvanchery Plant",
        "P3 - Guduvachery Plant": "P3 - Guduvanchery Plant",
        "P2&3 - Guduvachery Plants": "P2&3 - Guduvanchery Plants",
    }
    for old_value, new_value in replacements.items():
        for table_name in table_names:
            cursor.execute(
                f"UPDATE {table_name} SET plant = ? WHERE plant = ?",
                (new_value, old_value),
            )
    cursor.execute(
        "UPDATE system_logs SET details = REPLACE(details, ?, ?) WHERE details LIKE ?",
        ("Guduvachery", "Guduvanchery", "%Guduvachery%"),
    )


def _migrate_document_categories(cursor):
    """Assign every legacy document to a real Document Library category."""
    cursor.execute(
        """SELECT id, category, file_name, original_file_name,
                  document_number, department, customer
           FROM documents"""
    )
    for row in cursor.fetchall():
        record = dict(row)
        category = infer_document_category(record)
        if category != (record.get("category") or ""):
            cursor.execute(
                "UPDATE documents SET category = ? WHERE id = ?",
                (category, record["id"]),
            )


def _migrate_iatf_manual_to_qms(cursor):
    """Move legacy Core Tools/IATF Manual uploads into the QMS folder."""
    cursor.execute(
        """UPDATE documents
           SET category = 'qms'
           WHERE file_name IN (
               SELECT file_name FROM category_documents
               WHERE category = 'core_tools_manuals'
                 AND (sub_category = 'iatf_manual' OR sub_category LIKE 'iatf_manual:%')
           )"""
    )
    cursor.execute(
        """UPDATE category_documents
           SET category = 'qms', sub_category = 'iatf_manual'
           WHERE category = 'core_tools_manuals'
             AND (sub_category = 'iatf_manual' OR sub_category LIKE 'iatf_manual:%')"""
    )


def init_db():
    """Create and update the selected database schema."""
    if is_mysql():
        _ensure_mysql_database()

    connection = get_connection()
    try:
        cursor = connection.cursor()
        for statement in MYSQL_SCHEMA if is_mysql() else SQLITE_SCHEMA:
            cursor.execute(statement)
        _ensure_required_columns(cursor)
        _migrate_departments(cursor)
        _migrate_customers(cursor)
        _migrate_plants(cursor)
        _migrate_document_categories(cursor)
        _migrate_iatf_manual_to_qms(cursor)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
