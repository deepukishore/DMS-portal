"""Copy the existing SQLite portal data into the configured MySQL database."""

import argparse
import os
import sqlite3

from config import Config
from database import configure_database, get_connection, init_db, is_mysql


TABLES = [
    "users",
    "documents",
    "archive",
    "system_logs",
    "category_documents",
    "revision_history",
    "document_versions",
    "recently_viewed",
    "bookmarks",
    "notifications",
    "quarterly_document_reminders",
    "quarterly_recipient_reminders",
]


def _sqlite_rows(database_path, table_name):
    if not database_path or not os.path.exists(database_path):
        return []
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        if not exists:
            return []
        return [dict(row) for row in connection.execute(f"SELECT * FROM {table_name}")]
    finally:
        connection.close()


def _user_rows():
    """Merge central and legacy user stores, preferring richer legacy profiles."""
    users_by_email = {
        row["email"]: row
        for row in _sqlite_rows(Config.SQLITE_DB_PATH, "users")
    }
    users_by_email.update(
        {
            row["email"]: row
            for row in _sqlite_rows(Config.USER_DB_PATH, "users")
        }
    )
    return list(users_by_email.values())


def _destination_columns(cursor, table_name):
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return [row["Field"] for row in cursor.fetchall()]


def _upsert_rows(cursor, table_name, rows):
    if not rows:
        return 0

    destination_columns = _destination_columns(cursor, table_name)
    columns = [column for column in destination_columns if column in rows[0]]
    if not columns:
        return 0

    quoted_columns = ", ".join(f"`{column}`" for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    update_columns = [column for column in columns if column != "id"]
    assignments = ", ".join(
        f"`{column}` = VALUES(`{column}`)" for column in update_columns
    )
    query = (
        f"INSERT INTO `{table_name}` ({quoted_columns}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {assignments}"
    )
    values = [tuple(row.get(column) for column in columns) for row in rows]
    cursor.executemany(query, values)
    return len(values)


def migrate(replace=False):
    configure_database(Config.__dict__)
    if not is_mysql():
        raise RuntimeError(
            "Set DATABASE_ENGINE=mysql and the MYSQL_* environment variables before migrating."
        )

    init_db()
    destination = get_connection()
    try:
        cursor = destination.cursor()
        if replace:
            for table_name in reversed(TABLES):
                cursor.execute(f"DELETE FROM `{table_name}`")

        copied = {}
        for table_name in TABLES:
            rows = (
                _user_rows()
                if table_name == "users"
                else _sqlite_rows(Config.SQLITE_DB_PATH, table_name)
            )
            copied[table_name] = _upsert_rows(cursor, table_name, rows)

        destination.commit()
        return copied
    except Exception:
        destination.rollback()
        raise
    finally:
        destination.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate all Smart DMS records from SQLite to MySQL."
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Clear destination tables before copying the SQLite records.",
    )
    args = parser.parse_args()

    copied = migrate(replace=args.replace)
    print("MySQL migration completed:")
    for table_name, count in copied.items():
        print(f"  {table_name}: {count} record(s)")


if __name__ == "__main__":
    main()
