# Mock Data Setup Guide

## Overview

This guide explains how to populate your Smart DMS application with comprehensive mock data that showcases all features and makes it easy to understand the system.

## What's Included

The mock data includes:

### 📋 **10 Sample Users** (Different Roles & Departments)
- **Admin**: Diva Chandra - Quality Department
- **Managers**: Arun Kumar (Production), Vani Raj (Manufacturing), Meera Desai (Operations)
- **Approvers**: Sneha Patel (Engineering), Priya Nair (Procurement)
- **Regular Users**: Rahul Mehta (Safety), Karthik S (Maintenance), Vikram Sharma (R&D), Rajesh Singh (Stores)

### 📄 **20+ Sample Documents**
- Multiple approval statuses: ✅ Approved, ⏳ Pending, ❌ Rejected
- Across all 4 plants and multiple departments
- Multiple customers (Hyundai Motors, Tata Motors, Ashok Leyland, TVS Motors, Internal)
- Realistic filenames and document types (PDFs, Excel sheets, Zips, etc.)

### 📦 **5 Archived Documents**
- Documents moved to archive to showcase the archival feature
- Various statuses and time ranges

### 📋 **20+ System Logs**
- User login/logout activities
- Document upload/approval/rejection actions
- Archive operations
- Different timestamps to show activity timeline

### 🗂️ **Plant Assets & Customer Records**
- Pre-configured for all plants and departments
- Multiple file entries per department for browsing demo

## Quick Start

### Step 1: Initialize Database
```bash
# Run the database initialization (creates tables)
python app.py
# This will create smart_dms.db with empty tables
```

Or directly initialize:
```bash
python -c "from database import init_db; init_db()"
```

### Step 2: Seed Mock Data
```bash
# Run the seeding script
python seed_db.py
```

Expected output:
```
============================================================
Smart DMS - Database Seeding
============================================================

📝 Seeding users...
✓ Created user: Diva Chandra (diva@example.com)
✓ Created user: Arun Kumar (arun@example.com)
...

📄 Seeding documents...
✓ Created document: inspection_report_april_20.pdf - Status: Approved
✓ Created document: qa_audit_checklist.docx - Status: Pending
...

📦 Seeding archive...
✓ Archived document: inspection_report_q1_2026.pdf
...

📋 Seeding system logs...
✓ Created log: LOGIN by Diva Chandra
...

============================================================
✅ Database seeding completed successfully!
============================================================

Demo Users:
------------------------------------------------------------
  Email: diva@example.com
  Password: Pass@12345
  Role: Admin

  Email: arun@example.com
  Password: Prod@12345
  Role: Manager

  Email: sneha@example.com
  Password: Eng@12345
  Role: Approver

  Email: rahul@example.com
  Password: Safe@12345
  Role: User
```

### Step 3: Run the Application
```bash
python app.py
# Application will be available at http://localhost:5000
```

### Step 4: Login with Demo Credentials

Use any of these credentials to explore:

| Email | Password | Role | Best For Testing |
|-------|----------|------|-------------------|
| diva@example.com | Pass@12345 | Admin | All features, approvals, admin sections |
| arun@example.com | Prod@12345 | Manager | Document uploads, department views |
| sneha@example.com | Eng@12345 | Approver | Approval workflows, document review |
| rahul@example.com | Safe@12345 | User | Basic document viewing, upload |
| priya@example.com | Proc@12345 | Approver | Cross-department approvals |

## Features to Explore

### 🏠 **Dashboard**
- View recent document uploads
- Mix of Approved (✅), Pending (⏳), and Rejected (❌) documents
- Quick access to actions

### 📤 **Upload Documents**
- Upload new documents
- Select from multiple plants and departments
- Choose customer for the document
- Track approval status

### ✅ **Approvals**
- View pending documents waiting for approval
- Approve or reject documents with comments
- See approval history

### 📦 **Archives**
- Browse archived documents
- See documents with their original upload dates
- Track archival timeline

### 🏭 **Plant Assets**
- Browse documents by plant
- Filter by department
- View all plant-specific files

### 👥 **Customer Records**
- View documents organized by customer
- Multiple departments per customer
- Track customer-related documents

### 📊 **System Logs**
- Activity timeline showing all operations
- User login/logout tracking
- Document upload/approval history
- Archive operations

### 👤 **User Profile**
- View logged-in user details
- Plant and department information
- Role display

## Database Structure

The mock data is populated into these tables:

```
users
├── email (PRIMARY KEY)
├── name
├── user_id (UNIQUE)
├── emp_id
├── plant
├── department
├── password_hash
└── role

documents
├── id (PRIMARY KEY)
├── name
├── user_id
├── uploader_email
├── plant
├── department
├── customer
├── file_name
├── uploaded_at
├── approval_status (Pending/Approved/Rejected)
└── approval_updated_at

archive
├── id (PRIMARY KEY)
├── timestamp
├── file_name
├── plant
├── department
├── customer
├── uploaded_by
├── user_id
├── approval_status
└── original_upload_date

system_logs
├── id (PRIMARY KEY)
├── timestamp
├── user_name
├── user_id
├── action (LOGIN/LOGOUT/DOCUMENT_UPLOAD/DOCUMENT_APPROVED/DOCUMENT_REJECTED/ARCHIVE_DOCUMENT)
└── details
```

## Data Statistics

- **Users**: 1 Admin, 3 Managers, 2 Approvers, 4 Regular Users
- **Documents**: 20+ across 4 plants, 10 departments
- **Approval Mix**: 40% Approved, 45% Pending, 15% Rejected
- **Customers**: 4 external + Internal (5 total)
- **Archives**: 5 historical records
- **System Logs**: 20+ activity entries

## Resetting Mock Data

To clear and reseed the database:

```bash
# Delete the database file
rm smart_dms.db

# Reinitialize and seed
python -c "from database import init_db; init_db()" && python seed_db.py
```

Or delete `smart_dms.db` and `smart_dms.sqlite3` files, then run `python seed_db.py` again.

## Customizing Mock Data

To add more mock data, edit `seed_db.py`:

1. **Add more users**: Modify `seed_users()` function
2. **Add more documents**: Modify `seed_documents()` function
3. **Add more archive records**: Modify `seed_archive()` function
4. **Add more logs**: Modify `seed_system_logs()` function

Then run:
```bash
python seed_db.py
```

## Troubleshooting

### Issue: "Database is locked"
**Solution**: Close any other connections to the database and try again.

### Issue: "Users already exist"
**Solution**: The script checks for existing data before inserting. Delete `smart_dms.db` and rerun.

### Issue: Documents not showing in dashboard
**Solution**: Make sure `seed_db.py` ran successfully. Check the output for any errors.

### Issue: Login not working
**Solution**: 
- Clear browser cookies/cache
- Verify the email is exactly: `diva@example.com`
- Verify the password is exactly: `Pass@12345`

## Demo Workflow

### Suggested Demo Flow:
1. **Login** as Admin (diva@example.com)
2. **View Dashboard** - See mixed approval statuses
3. **Review Approvals** - Approve/Reject pending documents
4. **View Archives** - See archived documents
5. **Check Plant Assets** - Browse by plant and department
6. **Review Customer Records** - Explore by customer
7. **View System Logs** - See the activity timeline
8. **Logout** and login as different user to see role-based views

### Sample Actions:
- Approve pending quality document (Approve)
- Reject a document with comment (Reject)
- View archived documents by plant
- Check system logs for approval history
- Upload a new document with multiple customer options
- Switch between plants to see different documents

## Performance Notes

- Database uses SQLite for simplicity - good for demo/small deployments
- With 20+ documents, queries should be instant
- Mock data uses realistic file names and customer names
- Timestamps are staggered to show activity over time

## File Upload Features Demonstration

The mock data doesn't actually upload files, but the document records show:
- How the system tracks file metadata
- Different file types (.pdf, .xlsx, .docx, .zip)
- File organization by plant, department, and customer
- Approval workflow with status tracking

To actually upload files:
1. Click "Upload Documents"
2. Select a plant, department, customer
3. Choose a file from your computer
4. Submit
5. The file will be saved and appear in documents list

## Next Steps

After exploring the mock data:
1. Customize the data for your specific needs
2. Add more users from your organization
3. Update customer names to match your clients
4. Create plant-specific document categories
5. Set up approval hierarchies based on your workflow

---

**Happy exploring! 🚀**
