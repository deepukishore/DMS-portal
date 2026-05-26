# How to Apply Enhanced Mock Data

## Quick Start

Your `seed_db.py` file has been updated with **3x more mock data**. Follow these steps to apply it:

---

## Step 1: Delete Old Database

Navigate to your project directory and delete the old database file:

**Windows Command Prompt:**
```cmd
cd c:\Users\deepu\OneDrive\Desktop\dms_portal_test
del smart_dms.db
```

**Or manually:** Navigate to the folder and delete `smart_dms.db`

---

## Step 2: Run the Seeding Script

```bash
python seed_db.py
```

You should see output like:
```
============================================================
Smart DMS - Database Seeding
============================================================

📝 Seeding users...
✓ Created user: Diva Chandra (diva@example.com)
✓ Created user: Arun Kumar (arun@example.com)
[... more users ...]

📄 Seeding documents...
✓ Created document: inspection_report_april_20.pdf - Status: Approved
✓ Created document: qa_audit_checklist_v2.docx - Status: Pending
[... many more documents ...]

📦 Seeding archive...
✓ Archived document: inspection_report_q1_2026.pdf
[... more archived docs ...]

📋 Seeding system logs...
✓ Created log: LOGIN by Diva Chandra
[... activity logs ...]

============================================================
✅ Database seeding completed successfully!
============================================================
```

---

## Step 3: Start the Application

```bash
python app.py
```

Open your browser to: **http://localhost:5000**

---

## Step 4: Login and Explore

Use any of these demo accounts:

### Quick Test Accounts
- **Admin User**: `diva@example.com` / `Pass@12345` → Full system access
- **Approver**: `sneha@example.com` / `Eng@12345` → Can approve/reject documents
- **Manager**: `arun@example.com` / `Prod@12345` → Department leader
- **Regular User**: `vikram@example.com` / `Rd@12345` → Can upload documents

---

## What's New in the Enhanced Data

### 📊 More Users (15 total, +5 new)
Added: `deepak@`, `priyanka@`, `suresh@`, `anjali@`, `mohit@`

### 📄 More Documents (54 total, +32 new)
- 6 documents per department (previously 2-3)
- All 4 plants fully populated
- All 5 customers represented
- Mixed approval statuses throughout

### 📦 More Archives (10 total, +5 new)
- Realistic historical dates
- Various approval statuses
- Spans 30-90 days in the past

### 📋 More Logs (40+ entries, +20+ new)
- Realistic user activity patterns
- Login/logout events
- Document actions with timestamps
- IP address logging

---

## Testing All Features

With the enhanced data, you can now test:

### ✅ Dashboard
- Browse 54 documents across all plants/departments
- Use search with diverse document types
- Filter by plant, department, customer
- View mixed approval statuses

### ✅ Upload & Approvals
- Find 14 pending documents requiring approval
- Test approval workflow with multiple roles
- See 36 approved and 4 rejected documents
- Track approval history

### ✅ Plant Assets
- **P1 Trichy**: 15 documents across Quality, Manufacturing, R&D
- **P2 Guduvachery**: 18 documents across Production, Maintenance, Stores  
- **P3 Guduvachery**: 10 documents across Engineering, Operations
- **P4 Uttarakhand**: 11 documents across Safety, Procurement

### ✅ Customer Records
- Browse documents by **Hyundai Motors** (11 docs)
- View **Tata Motors** documents (10 docs)
- Check **Ashok Leyland** records (5 docs)
- Review **Internal** documents (26 docs)

### ✅ Archive & Restore
- View 10 archived documents
- Test restore functionality
- Check historical dates (30-90 days old)

### ✅ System Logs
- 40+ audit trail entries
- Filter by action type
- Track user activities across 3 days
- View IP address logging

### ✅ Profile & Roles
- Test as Admin (diva)
- Test as Approver (sneha)
- Test as Manager (arun)
- Test as Regular User (vikram)

---

## File Changes Summary

**Modified:** `seed_db.py`
- ✅ `seed_users()` - Added 5 new users (15 total)
- ✅ `seed_documents()` - Added 32 new documents (54 total)
- ✅ `seed_archive()` - Added 5 new archived records (10 total)
- ✅ `seed_system_logs()` - Added 20+ new log entries

**Created:** `MOCK_DATA_ENHANCED.md` - Comprehensive documentation

**Created:** `APPLY_ENHANCED_DATA.md` - This file

---

## Troubleshooting

### Issue: "Database is locked"
**Solution:** Make sure the Flask app is not running. Stop it before running seeding.

### Issue: "Table already exists"
**Solution:** This is normal - the script safely skips existing records. You can safely run it multiple times.

### Issue: "User already exists"
**Solution:** The script checks if users already exist and skips duplicates. This is intended behavior.

### Issue: Documents not showing in dashboard
**Solution:** 
1. Refresh the page (Ctrl+F5)
2. Check that you're logged in
3. Verify no filters are hiding all documents
4. Check browser console for errors

### Issue: Need to reset completely
**Solution:**
```cmd
# Delete both database files
del smart_dms.db
del data\smart_dms_users.sqlite3

# Restart application (will auto-create fresh DB)
python app.py

# Then reseed
python seed_db.py
```

---

## Verification Checklist

After applying enhanced data, verify:

- [ ] Dashboard shows **54 documents**
- [ ] Users page shows **15 users** (if available)
- [ ] Approvals shows **14 pending** documents
- [ ] Archive shows **10 archived** documents
- [ ] Plant Assets shows all **4 plants** with documents
- [ ] Customer Records shows all **5 customers** with documents
- [ ] System Log shows **40+ entries** with varied actions
- [ ] Can login with at least 3 different accounts
- [ ] Can filter documents by plant, department, customer
- [ ] Can search documents across all types

---

## Sample Testing Workflow

1. **Login as diva@example.com** (Admin)
   - View Dashboard → 54 documents
   - Check each plant in Plant Assets
   - Review System Log → 40+ entries

2. **Switch to arun@example.com** (Manager - Production)
   - View your Production documents
   - Check Approvals page
   - See your department's workload

3. **Switch to sneha@example.com** (Approver)
   - View Approvals → 14 pending
   - Approve/Reject a document
   - Check System Log for your action

4. **Switch to vikram@example.com** (User - R&D)
   - Upload a test document
   - See it in dashboard (Pending status)
   - Check System Log for your upload

---

## Need Help?

**For issues with the application:**
- Check Flask error messages in terminal
- Review browser console (F12)
- Check `smart_dms.db` exists in project directory

**For questions about the data:**
- See `MOCK_DATA_ENHANCED.md` for detailed breakdown
- Each document includes uploader, department, customer, and status

---

**You're ready to test the app with comprehensive mock data!** 🎉

Start with: `python app.py` then login to http://localhost:5000
