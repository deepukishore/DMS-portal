# Data Persistence Implementation

## Overview
All uploaded documents, archive records, and system logs are now persisted to a SQLite database (`smart_dms.db`). Data survives application restarts and user logout/login cycles.

## What Changed

### 1. New Database Module (`database.py`)
- Creates SQLite database with tables for:
  - `documents` - All uploaded files with approval status
  - `archive` - Soft-deleted documents
  - `system_logs` - Audit trail of all actions
  - `users` - User accounts (already existed in separate DB)
- Auto-initializes on first run with default admin user

### 2. Updated Services
- **DocumentService**: Now reads/writes to `documents` and `archive` tables
- **SystemLogService**: Logs all actions to `system_logs` table
- **UserStoreService**: Already used SQLite (no changes needed)

### 3. Database Files
- `smart_dms.db` - Main database (documents, archive, logs)
- `data/smart_dms_users.sqlite3` - User credentials (existing)

## Usage

### First Run
```bash
python app.py
```
The database will be created automatically with the default admin user:
- Email: `diva@example.com`
- Password: `Pass@12345`

### Data Persistence
- Upload files → Saved to database
- Logout → Data remains
- Restart app → All data intact
- Login again → See all previous uploads

### Backup
To backup all data, simply copy:
```bash
smart_dms.db
data/smart_dms_users.sqlite3
uploads/
```

## Migration Notes
- Old in-memory data (DASHBOARD_RECORDS, SYSTEM_LOGS, etc.) is no longer used
- `mock_data.py` now only contains static reference data (plants, departments, customers)
- No data migration needed - fresh start with empty database
