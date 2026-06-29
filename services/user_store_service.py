import os
import sqlite3
from datetime import datetime

from data.departments import LEGACY_DEPARTMENT_MAP, normalize_department
from data.mock_data import USERS


class UserStoreService:
    """Persists user profiles and credentials in a small SQLite database."""

    _db_path = None

    @staticmethod
    def init_app(app):
        UserStoreService._db_path = app.config["USER_DB_PATH"]
        os.makedirs(os.path.dirname(UserStoreService._db_path), exist_ok=True)
        UserStoreService._ensure_schema()
        UserStoreService._migrate_departments()
        UserStoreService._seed_users()

    @staticmethod
    def _connect():
        connection = sqlite3.connect(UserStoreService._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _ensure_schema():
        with UserStoreService._connect() as connection:
            connection.execute(
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
                    created_at TEXT NOT NULL
                )
                """
            )
            # Add mobile and avatar columns if they don't exist (migration)
            try:
                connection.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
            except Exception:
                pass
            try:
                connection.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
            except Exception:
                pass
            try:
                connection.execute("ALTER TABLE users ADD COLUMN qms_level TEXT NOT NULL DEFAULT 'L4'")
            except Exception:
                pass
            connection.commit()

    @staticmethod
    def _seed_users():
        with UserStoreService._connect() as connection:
            count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if count:
                return

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for email, user in USERS.items():
                connection.execute(
                    """
                    INSERT INTO users (
                        email, name, user_id, emp_id, plant, department, role, password_hash, created_at, qms_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        email,
                        user["name"],
                        user["user_id"],
                        user.get("emp_id", ""),
                        user.get("plant", ""),
                        normalize_department(user.get("department", "")),
                        user.get("role", "User"),
                        user["password_hash"],
                        now,
                        user.get("qms_level", "L4"),
                    ),
                )
            connection.commit()

    @staticmethod
    def _migrate_departments():
        with UserStoreService._connect() as connection:
            for old_value, new_value in LEGACY_DEPARTMENT_MAP.items():
                connection.execute(
                    "UPDATE users SET department = ? WHERE department = ?",
                    (new_value, old_value),
                )
            connection.commit()

    @staticmethod
    def get_user_by_email(email):
        with UserStoreService._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_user_by_genid(genid):
        with UserStoreService._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE emp_id = ?", (genid,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_users_by_role(role):
        with UserStoreService._connect() as connection:
            rows = connection.execute("SELECT * FROM users WHERE role = ? ORDER BY name ASC", (role,)).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_users_by_qms_level(qms_level):
        with UserStoreService._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM users WHERE qms_level = ? ORDER BY name ASC",
                (qms_level,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_admin_users():
        return UserStoreService.get_users_by_role("Admin")

    @staticmethod
    def get_all_users():
        with UserStoreService._connect() as connection:
            rows = connection.execute("SELECT * FROM users ORDER BY name ASC").fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def email_exists(email):
        return UserStoreService.get_user_by_email(email) is not None

    @staticmethod
    def create_user(name, email, password_hash, emp_id="", plant="", department="", mobile="", role="User"):
        user_id = UserStoreService._next_user_id()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with UserStoreService._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    email, name, user_id, emp_id, plant, department, mobile, role, password_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    name,
                    user_id,
                    emp_id,
                    plant,
                    normalize_department(department),
                    mobile,
                    role,
                    password_hash,
                    created_at,
                ),
            )
            connection.commit()

        return UserStoreService.get_user_by_email(email)

    @staticmethod
    def update_user_profile(email, name=None, plant=None, department=None, role=None, mobile=None):
        with UserStoreService._connect() as connection:
            existing = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if not existing:
                return None
            connection.execute(
                "UPDATE users SET name = ?, plant = ?, department = ?, role = ?, mobile = ? WHERE email = ?",
                (
                    name or existing["name"],
                    plant or existing["plant"],
                    department or existing["department"],
                    role or existing["role"],
                    mobile if mobile is not None else existing["mobile"],
                    email,
                ),
            )
            connection.commit()
        return UserStoreService.get_user_by_email(email)

    @staticmethod
    def update_avatar(email, filename):
        with UserStoreService._connect() as connection:
            connection.execute("UPDATE users SET avatar = ? WHERE email = ?", (filename, email))
            connection.commit()

    @staticmethod
    def update_password(email, password_hash):
        with UserStoreService._connect() as connection:
            cursor = connection.execute(
                "UPDATE users SET password_hash = ? WHERE email = ?",
                (password_hash, email),
            )
            connection.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _next_user_id():
        with UserStoreService._connect() as connection:
            rows = connection.execute("SELECT user_id FROM users").fetchall()

        max_id = 0
        for row in rows:
            user_id = row["user_id"] or ""
            digits = "".join(character for character in user_id if character.isdigit())
            if digits:
                max_id = max(max_id, int(digits))

        return f"U{max_id + 1:03d}"
