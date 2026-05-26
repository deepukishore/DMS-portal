# Quick Start - Testing Data Persistence

## Prerequisites
Make sure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```

## Option 1: Start with Mock Data (Recommended for Demo)

### Step 1: Initialize and Seed Database
```bash
# This populates the database with comprehensive mock data
python seed_db.py
```

You'll see:
```
============================================================
Smart DMS - Database Seeding
============================================================

📝 Seeding users...
✓ Created user: Diva Chandra (diva@example.com)
[... more users ...]

📄 Seeding documents...
✓ Created document: inspection_report_april_20.pdf - Status: Approved
[... more documents ...]

📦 Seeding archive...
✓ Archived document: inspection_report_q1_2026.pdf
[... more archives ...]

📋 Seeding system logs...
✓ Created log: LOGIN by Diva Chandra
[... more logs ...]

============================================================
✅ Database seeding completed successfully!
============================================================
```

### Step 2: Start the Application
```bash
python app.py
```

### Step 3: Login with Demo Account
- Open http://localhost:5000
- Email: `diva@example.com` (Admin - full access)
- Password: `Pass@12345`

### Step 4: Explore the Features

**Dashboard**: See 20+ documents with mixed approval statuses (Approved ✅, Pending ⏳, Rejected ❌)

**Approvals**: View and approve/reject pending documents

**Plant Assets**: Browse documents organized by plant and department

**Customer Records**: View documents grouped by customer

**Archives**: See archived documents with history

**System Logs**: Track user activities and document operations

**Upload**: Add your own documents

**For more mock data options**, see [MOCK_DATA_SETUP.md](MOCK_DATA_SETUP.md)

---

## Option 2: Start Fresh with Empty Database

### Step 1: Start the Application
```bash
python app.py
```

### Step 2: Login
- Open http://localhost:5000
- Email: `diva@example.com`
- Password: `Pass@12345`

### Step 3: Upload a File
1. Go to "Upload" page
2. Select plant, department, customer
3. Drag and drop any file
4. Click "Upload Files"
5. Note the file name and details

### Step 4: Verify Upload
1. Go to "Dashboard" page
2. You should see your uploaded file with "Pending" status

### Step 5: Test Persistence - Logout
1. Click "Logout" in the top right
2. You're now logged out

### Step 6: Test Persistence - Login Again
1. Login again with same credentials
2. Go to "Dashboard"
3. **Your uploaded file is still there!** ✓

### Step 7: Test Persistence - Restart App
1. Stop the Flask app (Ctrl+C)
2. Start it again: `python app.py`
3. Login and check Dashboard
4. **All your data is still there!** ✓

---

## What's Persisted?
- ✓ All uploaded documents
- ✓ Approval statuses (Pending/Approved/Rejected)
- ✓ Archive records (deleted files)
- ✓ System logs (all user actions)
- ✓ User accounts

## Database Location
All data is stored in:
- `smart_dms.db` - Main database
- `data/smart_dms_users.sqlite3` - User credentials
- `uploads/` - Actual uploaded files

## Demo Users (After Seeding)

| Email | Password | Role | Department |
|-------|----------|------|-----------|
| diva@example.com | Pass@12345 | Admin | Quality |
| arun@example.com | Prod@12345 | Manager | Production |
| sneha@example.com | Eng@12345 | Approver | Engineering |
| rahul@example.com | Safe@12345 | User | Safety |

## Resetting Data
To clear all data and start fresh:
```bash
# Option 1: Delete and let app recreate
rm smart_dms.db smart_dms_users.sqlite3

# Option 2: Reseed with fresh mock data
rm smart_dms.db
python seed_db.py
```

## Backup Your Data
To backup everything:
```bash
# Copy these files
smart_dms.db
data/smart_dms_users.sqlite3
uploads/
```
