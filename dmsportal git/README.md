![1778754023805](image/README/1778754023805.png)![1778754027776](image/README/1778754027776.png)# Smart DMS v2.0 — Manufacturing Document Management Portal

A Flask-based Industry 4.0 Document Management System with full audit logging,
plant asset browsing, customer records, drag-and-drop upload, and more.

---

## Plants

| ID | Plant | Location |
|----|-------|----------|
| P1 | Trichy Plant | Trichy, Tamil Nadu |
| P2 | Guduvachery Plant | Guduvachery, Tamil Nadu |
| P3 | Guduvachery Plant | Guduvachery, Tamil Nadu |
| P4 | Uttarakhand Plant | Uttarakhand |

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

Open http://localhost:5000

**Demo credentials:** `diva@example.com` / `Pass@12345`

---

## Features

| Feature | Description |
|---------|-------------|
| Login / Register | Separate register page linked from login |
| Forgot Password | Token-based reset link (printed to terminal if SMTP not configured) |
| Master Dashboard | Full table with search, plant/dept filter, and **Delete** action |
| Upload | Drag-and-drop multi-file upload, any format, 100 MB limit |
| Approvals | Approved / Pending / Denied badge statuses |
| Archive | Soft-deleted documents with restore button |
| Plant Assets | Click plant card → department tabs → view-only file list |
| Customer Records | Same UX as Plant Assets — Hyundai, Tata, Ashok Leyland, TVS Motors |
| System Log | Full audit trail: login, logout, register, upload, view, delete — filterable by action type |
| **Data Persistence** | All data saved to SQLite database — survives restarts and logout/login |

---

## Project Structure

```
smart_dms_v2/
├── app.py                      # Flask factory
├── config.py                   # Config via env vars
├── extensions.py               # Flask-Mail instance
├── database.py                 # SQLite database setup
├── requirements.txt
├── smart_dms.db                # SQLite database (auto-created)
│
├── data/
│   ├── mock_data.py            # Static reference data (plants, departments, customers)
│   └── smart_dms_users.sqlite3 # User credentials database
│
├── routes/                     # One Blueprint per page
│   ├── auth_routes.py
│   ├── dashboard_routes.py
│   ├── upload_routes.py
│   ├── approval_routes.py
│   ├── archive_routes.py
│   ├── plant_assets_routes.py
│   ├── customer_records_routes.py
│   └── system_log_routes.py
│
├── services/                   # One class per domain
│   ├── auth_service.py
│   ├── document_service.py
│   ├── plant_asset_service.py
│   ├── customer_record_service.py
│   ├── system_log_service.py
│   ├── mail_service.py
│   └── password_reset_service.py
│
├── templates/
│   ├── layout.html             # Shared shell with sidebar + topbar
│   ├── dashboard.html
│   ├── upload.html
│   ├── approvals.html
│   ├── archive.html
│   ├── plant_assets.html
│   ├── customer_records.html
│   ├── system_log.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── reset_password.html
│   └── components/
│       └── sidebar.html
│
├── static/
│   ├── css/app.css             # Dark industrial theme (IBM Plex fonts)
│   └── js/
│       ├── app.js              # Alert auto-dismiss, modal close
│       ├── upload.js           # Drag-and-drop file handling
│       ├── plant_assets.js     # Plant → dept → files AJAX
│       └── customer_records.js # Customer → dept → files AJAX
│
└── uploads/                    # Uploaded files saved here
```

---

## Environment Variables (optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `smart-dms-secret-key-change-in-production` | Flask sessions |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP host |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USERNAME` | _(empty)_ | SMTP username |
| `MAIL_PASSWORD` | _(empty)_ | SMTP password |

If mail is not configured, password reset links are printed to the terminal.

---

## Roadmap

- [x] SQLite persistence for documents, archive, and system logs
- [ ] Role-based access control (Admin / QA / Operator / Viewer)
- [ ] Real file download / in-browser viewer endpoint
- [ ] CSV export for dashboard and system log
- [ ] Document versioning
- [ ] Dockerize for deployment
