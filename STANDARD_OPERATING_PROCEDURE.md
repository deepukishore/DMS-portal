# Smart DMS v2.0 — Standard Operating Procedure (SOP)

## 1. Purpose

This SOP defines the approved procedures for operating, uploading, approving, and maintaining the Smart DMS Document Management Portal.

## 2. Scope

Applies to all users, approvers, managers, and administrators who interact with the Smart DMS portal for document submission, approval, library storage, and audit tracking.

## 3. Definitions

- **Uploader**: A user who submits documents through the Upload page.
- **Approver**: A user or designated email recipient who reviews and approves uploaded documents.
- **Document Library**: The category-based repository where uploaded documents are stored and organized.
- **Pending**: Document status assigned to files that have been uploaded and await approval.
- **Archive**: Soft-deleted documents retained for audit and restore.

## 4. System Overview

Smart DMS is a Flask-based portal using SQLite databases and Jinja templates. Key components include:

- `app.py` — application factory and blueprint registration
- `routes/` — UI endpoints for login, upload, approvals, library, dashboard, and more
- `services/` — business logic for authentication, document handling, email, logging, and notifications
- `templates/` — HTML pages rendered by Jinja2
- `static/js/upload.js` — upload validation and library path selection
- `uploads/` — physical storage location for uploaded files

## 5. Pre-Requisites

Before using the portal:

1. Ensure the Python virtual environment is created and activated.
2. Install dependencies with `pip install -r requirements.txt`.
3. Confirm config values in `config.py` or environment variables.
4. Start the app using `python app.py`.
5. Open the portal at `http://localhost:5001`.

## 6. User Roles and Access

- **Admin** — full access, including user management, category library, log access, and approval actions.
- **Manager** — broad access to documents, approvals, dashboards, and archive actions.
- **Approver** — review and decide on pending document uploads.
- **User** — upload documents, view own submissions, and access documents they are allowed to see.

## 7. Daily Operational Procedure

### 7.1 Start the Portal

1. Activate the Python virtual environment.
2. Run `python app.py`.
3. Confirm the application starts successfully on `http://localhost:5001`.
4. Verify the `uploads/` folder exists and is writable.

### 7.2 Login

1. Open the portal URL in a browser.
2. Enter your email or employee ID and password.
3. If using the employee ID, enter the numeric/GENID value in the username field.
4. Click **Login**.

### 7.3 Upload Documents

1. Navigate to **Upload Documents**.
2. Drag-and-drop files into the upload area or click to browse.
3. Confirm accepted file types: `.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`.
4. Enter the **Document Number** (required).
5. Optionally enter the **Revision Number**; if omitted, `Rev.00` is used.
6. Select the correct **Plant** and **Department**.
7. Choose a **Customer**, or enable **Internal Document** to mark it internal.
8. Select the correct **Category** and then the exact **Folder/Subcategory** path.
9. Optionally enable **Revision Summary** and add a change note.
10. Click **Submit for Approval**.

**Important:** All uploads go into the Document Library and are sent for approval; there is no alternate upload path.

### 7.4 Approvals and Review

1. Navigate to **Pending Items (Approvals)**.
2. Use the filter tabs to view documents by status: Pending, Approved, or Rejected.
3. Click **Review** on a pending document.
4. Inspect document metadata, preview the file if available, and read any revision summary.
5. Choose **Approve** or **Reject**.
6. If rejecting, add a rejection note describing required changes.
7. The uploader receives notification and email of the decision.

### 7.5 Document Library Management

1. Open **Document Library**.
2. Browse categories and folders to locate stored files.
3. Use the search and filtering controls to narrow results by category, plant, department, or customer.
4. Download approved documents for reference as needed.

### 7.6 Archive and Audit

1. Deleted documents move to **Archive** rather than being permanently removed.
2. Use **System Log** to review upload events, approval actions, and user activity.
3. Check **Revision History** for records of document updates and summaries.

## 8. Maintenance Procedure

### 8.1 Database and Upload Backup

- Backup `smart_dms.db` and `data/smart_dms_users.sqlite3` regularly.
- Backup the `uploads/` folder to preserve all stored documents.

### 8.2 Seeding and Reset

- Use `seed_db.py` or `reset_and_seed.py` to recreate or reseed the database with mock/demo data.
- Always backup the current database before running reset scripts.

### 8.3 Email Configuration

- Confirm SMTP credentials and sender address in environment variables or `config.py`.
- If email fails, password reset and approval links may be printed to the console in development.

### 8.4 Logging and Notifications

- Monitor `system_logs` for failed uploads, approval email failures, and access issues.
- Confirm in-app notifications appear for upload submitters and approvers.

## 9. Troubleshooting

### 9.1 Upload fails

- Verify the selected category and folder path are both chosen.
- Confirm all required metadata fields are completed.
- Check that file types and sizes are within allowed limits.
- Inspect the Flask terminal for error messages.

### 9.2 Approval email not delivered

- Confirm `APPROVAL_RECIPIENT`, `MAIL_SERVER`, `MAIL_USERNAME`, and `MAIL_PASSWORD` are configured correctly.
- Check spam/junk folder.
- Review the application console output for SMTP errors.

### 9.3 Application fails to start

- Ensure required Python packages are installed.
- Confirm the virtual environment is activated.
- Check for port conflicts on `5001`.

## 10. Change Control

- Any change to form validation, upload behavior, or approval logic must be tested end-to-end.
- Document all release changes in the project `README.md` and update this SOP when upload or approval process changes.

---

**Document Owner:** Smart DMS Implementation Team

**Last Updated:** 2026-06-08
