# Smart DMS — Flask Document Management Portal

Smart DMS is the current Flask-based document management portal used for document upload, approval, library browsing, records access, reporting, and audit logging.

## What the app does
- Supports user login with email or employee ID (GENID)
- Allows document upload with metadata and approval workflow
- Provides a dashboard for search, filtering, status tracking, bookmarks, and recent documents
- Includes approval review pages for first-stage and final-stage review
- Offers document library browsing, procedures, plant records, and customer records
- Includes revision history, archive, system log, notifications, and profile management

## Current modules
- Authentication: login, registration, password reset, logout
- Dashboard: searchable document overview and exports
- Upload: guided upload with category and library folder selection
- Approvals: review and decision workflow with secure review links
- Document Library: category-based browsing for reference documents
- Procedures: management, customer, support, and plant procedure sections
- Tracking and Notifications: approval tracking and in-app notifications
- Reports: graphics report, revision history, archive, and system log
- Profile and People: user directory and profile management

## Run locally
`powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
`

Open http://localhost:5001

## Main routes
- /login or /
- /register
- /forgot-password
- /reset-password/<token>
- /dashboard
- /upload
- /approvals
- /document-library
- /procedures
- /plant-assets
- /customer-records
- /graphics-report
- /revision-history
- /archive
- /system-log
- /people
- /profile

## Current access model
- User: can sign in, upload documents, and view dashboard content
- Approver: can review documents and make approval decisions
- Supervisor / Manager / Admin: have broader oversight and admin-facing access

## Storage and data
- Main database: smart_dms.db
- User credential database: data/smart_dms_users.sqlite3
- Uploads folder: uploads/

## Notes
- The app works with SQLite by default and can be configured for MySQL through the environment settings.
- If the database is empty, the app falls back to mock data for demonstrations.
- Mail and reset links depend on the configured SMTP settings.
