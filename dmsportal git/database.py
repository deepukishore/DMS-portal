import sqlite3
import json
from datetime import datetime
from data.customers import LEGACY_CUSTOMER_MAP
from data.departments import LEGACY_DEPARTMENT_MAP, normalize_department
from werkzeug.security import generate_password_hash

DB_PATH = 'smart_dms.db'


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


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            user_id TEXT UNIQUE NOT NULL,
            emp_id TEXT,
            plant TEXT,
            department TEXT,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'User'
        )
    ''')
    
    # Documents table
    cursor.execute('''
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
            approval_updated_at TEXT
        )
    ''')

    # Notifications table
    cursor.execute('''
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
    ''')
    
    # Archive table
    cursor.execute('''
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
    ''')
    
    # System logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT
        )
    ''')
    
    # Category documents table
    cursor.execute('''
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
    ''')
    
    # Revision history table
    cursor.execute('''
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
    ''')

    # Document versions table (stores all versions of a document)
    cursor.execute('''
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
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    ''')

    # Recently viewed table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recently_viewed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            document_id INTEGER NOT NULL,
            viewed_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    ''')

    # Bookmarks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            document_id INTEGER NOT NULL,
            bookmarked_at TEXT NOT NULL,
            UNIQUE(user_email, document_id)
        )
    ''')

    # Add pdf_file_name and original_file_name columns to documents if not exist
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN pdf_file_name TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN original_file_name TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN current_version INTEGER DEFAULT 1')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN category TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN document_number TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN revision_number TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN rejection_comment TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE documents ADD COLUMN decision_by TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE document_versions ADD COLUMN document_number TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE document_versions ADD COLUMN revision_number TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE document_versions ADD COLUMN category TEXT')
    except Exception:
        pass

    conn.commit()
    
    # Insert default user if not exists
    cursor.execute('SELECT email FROM users WHERE email = ?', ('diva@example.com',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (email, name, user_id, emp_id, plant, department, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'diva@example.com',
            'Diva Chandra',
            'U001',
            'EMP001',
            'P1 - Trichy Plant',
            normalize_department('Quality'),
            generate_password_hash('Pass@12345'),
            'Admin'
        ))
        conn.commit()

    _migrate_departments(cursor)
    _migrate_customers(cursor)
    conn.commit()
    
    conn.close()
