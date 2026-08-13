import os
import sqlite3
from datetime import datetime

from database import get_connection
from data.departments import LEGACY_DEPARTMENT_MAP, normalize_department
from data.mock_data import USERS


class UserStoreService:
    """Persists profiles and credentials in the portal's central database."""

    _legacy_db_path = None
    QMS_LEVELS = {"L1", "L2", "L3", "L4"}

    @staticmethod
    def init_app(app):
        UserStoreService._legacy_db_path = app.config.get("USER_DB_PATH")
        UserStoreService._migrate_legacy_users()
        UserStoreService._migrate_departments()
        UserStoreService._seed_users()

    @staticmethod
    def _connect():
        return get_connection()

    @staticmethod
    def _migrate_legacy_users():
        """Copy users from the former standalone SQLite user store once."""
        legacy_path = UserStoreService._legacy_db_path
        if not legacy_path or not os.path.exists(legacy_path):
            return

        legacy_connection = sqlite3.connect(legacy_path)
        legacy_connection.row_factory = sqlite3.Row
        try:
            table = legacy_connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'users'"
            ).fetchone()
            if not table:
                return
            legacy_users = legacy_connection.execute("SELECT * FROM users").fetchall()
        finally:
            legacy_connection.close()

        with UserStoreService._connect() as connection:
            for legacy_user in legacy_users:
                user = dict(legacy_user)
                existing = connection.execute(
                    "SELECT email FROM users WHERE email = ?",
                    (user["email"],),
                ).fetchone()
                if existing:
                    continue
                connection.execute(
                    """
                    INSERT INTO users (
                        email, name, user_id, emp_id, plant, department, mobile,
                        role, password_hash, created_at, avatar, qms_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user["email"],
                        user["name"],
                        user["user_id"],
                        user.get("emp_id", ""),
                        user.get("plant", ""),
                        normalize_department(user.get("department", "")),
                        user.get("mobile", ""),
                        user.get("role", "User"),
                        user["password_hash"],
                        user.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        user.get("avatar"),
                        user.get("qms_level", "L4"),
                    ),
                )
            connection.commit()

    @staticmethod
    def _seed_users():
        with UserStoreService._connect() as connection:
            count_row = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()
            count = count_row["count"]
            if count:
                return

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for email, user in USERS.items():
                connection.execute(
                    """
                    INSERT INTO users (
                        email, name, user_id, emp_id, plant, department, mobile,
                        role, password_hash, created_at, qms_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        email,
                        user["name"],
                        user["user_id"],
                        user.get("emp_id", ""),
                        user.get("plant", ""),
                        normalize_department(user.get("department", "")),
                        user.get("mobile", ""),
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
    def create_user(
        name,
        email,
        password_hash,
        emp_id="",
        plant="",
        department="",
        mobile="",
        role="User",
        qms_level="L4",
    ):
        user_id = UserStoreService._next_user_id()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with UserStoreService._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    email, name, user_id, emp_id, plant, department, mobile,
                    role, password_hash, created_at, qms_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    qms_level,
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
    def update_qms_level(email, qms_level):
        """Update a non-admin user's QMS access level."""
        normalized_level = str(qms_level or "").strip().upper()
        if normalized_level not in UserStoreService.QMS_LEVELS:
            raise ValueError("QMS level must be L1, L2, L3, or L4.")

        connection = UserStoreService._connect()
        try:
            existing = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            if not existing:
                return None
            if existing["role"] == "Admin" and normalized_level != "L1":
                raise ValueError("Admin accounts are always assigned QMS level L1.")
            connection.execute(
                "UPDATE users SET qms_level = ? WHERE email = ?",
                (normalized_level, email),
            )
            connection.commit()
            updated = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            return dict(updated) if updated else None
        finally:
            connection.close()

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
