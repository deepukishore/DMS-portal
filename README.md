# Smart DMS

Smart DMS is a Flask-based document management portal for controlled document upload, staged approval, library browsing, revision tracking, reporting, and audit logging.

## Features

- Sign in with an email address or employee ID (GEN ID)
- Upload PDF, Word, Excel, and PowerPoint documents with document-control metadata
- Route documents through L2 and L1 approval stages
- Browse approved documents by QMS category, plant, department, customer, and procedure type
- Preview documents, track revisions, bookmark records, and review recent activity
- Export dashboard and approval data
- Manage notifications, user profiles, QMS levels, archives, and system logs
- Run with SQLite locally or MySQL in a shared environment

## Technology

- Python and Flask
- SQLite by default, with optional MySQL support through PyMySQL
- Jinja templates, vanilla JavaScript, and CSS
- python-docx, openpyxl, python-pptx, ReportLab, PyMuPDF, and pypdf for document handling and previews

## Project structure

```text
app.py                     Application factory and Flask entry point
config.py                  Environment-based application configuration
database.py                SQLite/MySQL schema and database helpers
routes/                    HTTP routes grouped by feature
services/                  Business logic and document-processing services
data/                      Reference data and local user database
templates/                 Jinja HTML templates
static/                    CSS, JavaScript, images, and user avatars
uploads/                   Runtime document storage (contents are ignored by Git)
download_templates/        Downloadable document-library templates
tests/                     Automated tests
```

## Local setup

Python 3.10 or newer is recommended.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open <http://localhost:5001>.

The app creates the required SQLite tables during startup. Existing local data is read from `smart_dms.db` and `data/smart_dms_users.sqlite3`.

## Configuration

Configuration is loaded from environment variables and an optional `.env` file. Never commit `.env` or production credentials.

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session signing key | Development-only fallback |
| `PORT` | Local web server port | `5001` |
| `DATABASE_ENGINE` | `sqlite` or `mysql` | `sqlite` |
| `MYSQL_HOST` | MySQL server hostname | `127.0.0.1` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | Empty |
| `MYSQL_DATABASE` | MySQL database name | `smart_dms` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | SMTP account | Application fallback |
| `MAIL_PASSWORD` | SMTP password or app password | Application fallback |
| `MAIL_DEFAULT_SENDER` | Sender used for portal mail | Mail username fallback |
| `FIRST_APPROVAL_RECIPIENT` | First-stage approval mailbox | Application fallback |
| `FINAL_APPROVAL_RECIPIENT` | Final-stage approval mailbox | Application fallback |
| `REVIEW_TOKEN_SALT` | Salt for signed approval links | Development fallback |
| `PORTAL_BASE_URL` | Public base URL used in reminder email links | `http://127.0.0.1:5001` |
| `QUARTERLY_REMINDERS_ENABLED` | Enable automatic quarterly document-review emails | `true` |
| `QUARTERLY_REMINDER_HOUR` | Local server hour for reminders on each quarter's first day | `9` |

For MySQL, set `DATABASE_ENGINE=mysql` and the `MYSQL_*` values before starting the app. To copy existing SQLite records into the configured MySQL database, run:

```powershell
python migrate_to_mysql.py
```

Use `python migrate_to_mysql.py --replace` only when the destination tables should be cleared before migration.

## Testing

Run the standard-library test suite with:

```powershell
python -m unittest discover -s tests -v
```

Some lightweight structure tests use pytest-style functions. If pytest is available, run the complete suite with:

```powershell
python -m pytest
```

## Main application areas

- `/dashboard` - document overview, search, filters, export, and bookmarks
- `/upload` - controlled document upload and metadata entry
- `/approvals` - approval queue, review, decisions, and resubmission
- `/tracking` - document approval tracking
- `/document-library` - approved reference-document library
- `/procedures`, `/plant-assets`, and `/customer-records` - specialized record browsers
- `/graphics-report`, `/revision-history`, `/archive`, and `/system-log` - reporting and audit views
- `/people` and `/profile` - users, access levels, and account settings

## Operational notes

- Uploaded files and local databases are runtime data and are intentionally excluded from Git.
- PowerPoint previews use Microsoft PowerPoint on Windows when available; otherwise the app creates a text-based PDF preview.
- SMTP must be configured with valid credentials for password resets and approval emails.
- Quarterly reminders run on January 1, April 1, July 1, and October 1. Run `flask --app app send-quarterly-reminders` to send any unsent reminders for the current quarter manually.
- Replace all development fallback secrets and mail settings before deployment.

Additional project documentation is available in [USER_MANUAL.md](USER_MANUAL.md) and [DMS_PORTAL_UPDATED_PROCESS_FLOW.md](DMS_PORTAL_UPDATED_PROCESS_FLOW.md).
