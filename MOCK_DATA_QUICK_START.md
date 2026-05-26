# Smart DMS Mock Data - Quick Start Guide

Your application is now loaded with comprehensive mock data! Here's everything you need to know.

---

## 🚀 Quick Start

### 1. Start the Application
```bash
python app.py
```

### 2. Open Browser
Navigate to: **http://localhost:5000**

### 3. Login with Demo Account
```
Email: diva@example.com
Password: Pass@12345
```

---

## 👥 Available Demo Users

| Email | Password | Role | Plant | Department |
|-------|----------|------|-------|-----------|
| diva@example.com | Pass@12345 | Admin | P1 - Trichy Plant | Quality |
| arun@example.com | Prod@12345 | Manager | P2 - Guduvachery Plant | Production |
| sneha@example.com | Eng@12345 | Approver | P3 - Guduvachery Plant | Engineering |
| rahul@example.com | Safe@12345 | User | P4 - Uttarakhand Plant | Safety |
| vani@example.com | Mfg@12345 | Manager | P1 - Trichy Plant | Manufacturing |
| karthik@example.com | Maint@12345 | User | P2 - Guduvachery Plant | Maintenance |
| priya@example.com | Proc@12345 | Approver | P4 - Uttarakhand Plant | Procurement |
| vikram@example.com | Rd@12345 | User | P1 - Trichy Plant | R&D |
| meera@example.com | Manager@12345 | Manager | P3 - Guduvachery Plant | Operations |
| rajesh@example.com | User@12345 | User | P2 - Guduvachery Plant | Stores |

---

## 📊 Mock Data Summary

### Users
- **Total**: 10 users
- **Roles**: 1 Admin, 3 Managers, 2 Approvers, 4 Regular Users
- **Plants**: Distributed across all 4 plants
- **Departments**: 10+ different departments

### Documents
- **Total**: 22 documents
- **Status Distribution**:
  - Approved: 12 (55%)
  - Pending: 8 (36%)
  - Rejected: 2 (9%)
- **By Plant**:
  - P1 - Trichy Plant: 9 docs
  - P2 - Guduvachery Plant: 7 docs
  - P3 - Guduvachery Plant: 3 docs
  - P4 - Uttarakhand Plant: 3 docs

### Archives
- **Total**: 5 archived documents
- **Historical records**: Soft-deleted documents with restore capability

### System Logs
- **Total**: 24 log entries
- **Activity Types**:
  - LOGIN: 8
  - LOGOUT: 4
  - UPLOAD: 2
  - VIEW: 5
  - APPROVED: 3
  - REJECTED: 1
  - APPROVAL_EMAIL: 1

---

## 🎯 Features to Explore

### 1. **Dashboard**
- View mixed approval statuses (Approved, Pending, Rejected)
- Filter by Plant and Department
- Search documents
- Delete/Archive documents

**What to do**:
- Login → See documents with various statuses
- Use filters to narrow down by plant/department
- Try deleting a document

### 2. **Upload**
- Drag-and-drop multi-file upload (100 MB limit)
- Supports any file format
- Automatic approval workflow

**What to do**:
- Upload a sample file
- See it appear in dashboard with "Pending" status
- Follow the approval workflow

### 3. **Approvals**
- View pending approval documents
- Approve/Reject with reasons
- Track approval history

**What to do**:
- Switch to admin account (diva@example.com)
- View 8 pending documents
- Try approving/rejecting one

### 4. **Archive**
- View soft-deleted documents
- Restore archived files
- Historical record keeping

**What to do**:
- Delete a document from dashboard
- Visit Archive page
- Try restoring it

### 5. **Plant Assets**
- Browse documents by plant
- View departments within each plant
- Department-specific file listings

**What to do**:
- Click on a plant card
- Expand different departments
- View documents in each

### 6. **Customer Records**
- Documents grouped by customer
- Hyundai, Tata, Ashok Leyland, TVS Motors, Internal
- Department filters per customer

**What to do**:
- Click on a customer
- View department-specific documents
- Compare documents across customers

### 7. **System Log**
- Complete audit trail
- Filter by action type
- Track user activities

**What to do**:
- View login/logout events
- See upload activities
- Check approval actions
- Filter by action type

### 8. **Profile**
- View current user details
- Department and plant information
- User role display

---

## 🔍 Sample Document Types

### Quality Department
- `inspection_report_april_20.pdf`
- `qa_audit_checklist.docx`

### Production
- `assembly_line_daily_report.xlsx`
- `shift_production_metrics.xlsx`

### Engineering
- `cad_revision_v5.pdf`
- `tooling_design_package.zip`

### Safety
- `safety_audit_q2_report.pdf`
- `incident_investigation_report.pdf`

### Manufacturing
- `production_schedule_april.xlsx`
- `machine_utilization_report.pdf`

### Maintenance
- `preventive_maintenance_log.pdf`
- `equipment_breakdown_analysis.xlsx`

### R&D
- `prototype_testing_results.pdf`

### Operations
- `ops_dashboard_extract.pdf`

### Procurement
- `vendor_contracts_q2.pdf`

### Stores
- `inventory_stock_report.xlsx`
- `material_inward_receipt.pdf`

---

## 💡 Testing Workflows

### Approval Workflow
1. Upload document as regular user → Status: "Pending"
2. Switch to approver account → View in Approvals
3. Approve/Reject → Status updates
4. Back in dashboard → See updated status

### Plant Navigation
1. Click any plant card
2. Select department tab
3. View files in that department
4. Click file to view details

### Archive Workflow
1. Dashboard → Delete document
2. Archive page → Document appears
3. Click Restore → Returns to dashboard (Pending status)
4. Confirm it's back in main list

### Search & Filter
1. Dashboard → Use search box
2. Type partial filename → Results filter
3. Use Plant filter → See that plant's docs
4. Use Department filter → See that dept's docs

---

## 📋 Document Fields

Each document has:
- **ID**: Unique identifier
- **Name**: Filename and description
- **Uploader**: User who uploaded
- **Plant**: Manufacturing location
- **Department**: Functional area
- **Customer**: External customer (or Internal)
- **File Name**: Actual file name
- **Uploaded At**: Timestamp
- **Approval Status**: Approved/Pending/Rejected
- **Approval Updated At**: Last status change timestamp

---

## 🔄 Resetting Mock Data

If you want a fresh start:

### Option 1: Delete and Reseed
```bash
# Delete the database
rm smart_dms.db

# Reinitialize with fresh data
python seed_db.py

# Start application
python app.py
```

### Option 2: Clear All Data
```bash
# Delete all database files
rm smart_dms.db smart_dms_users.sqlite3

# Application will auto-create fresh DB
python app.py
```

### Option 3: Just Reseed (preserves new uploads)
```bash
python seed_db.py
```

---

## 🛠️ Customization

### Add More Users
Edit `database.py` → Add to users list in `init_db()`

### Add More Documents
Edit `seed_db.py` → Add to documents list in `seed_documents()` function

### Modify Existing Data
Edit source files and reseed

---

## 📈 Data Statistics

| Metric | Value |
|--------|-------|
| Total Users | 10 |
| Total Documents | 22 |
| Approved Documents | 12 |
| Pending Documents | 8 |
| Rejected Documents | 2 |
| Archived Documents | 5 |
| System Log Entries | 24 |
| Plants | 4 |
| Departments | 10+ |
| Customers | 5 (4 External + Internal) |

---

## ✅ What You Can Now Do

- [x] See a realistic DMS with mixed data
- [x] Test approval workflows
- [x] Browse by plant and department
- [x] View customer-specific documents
- [x] Upload and track new documents
- [x] Archive and restore files
- [x] View complete audit logs
- [x] Test different user roles
- [x] Search and filter documents
- [x] Test all application features

---

## 🎓 Learning Path

1. **Start**: Login as Admin (diva@example.com)
2. **Explore**: Visit each page to see structure
3. **Filter**: Use search and filters to narrow down data
4. **Test**: Try uploading a new document
5. **Approve**: Switch roles and test approval workflow
6. **Archive**: Delete and restore documents
7. **Logs**: Review system activities

---

## 🆘 Troubleshooting

### "No documents showing"
- Make sure you're logged in
- Check plant/department filters
- Try searching with empty search box
- Refresh the page

### "User login fails"
- Verify email is typed correctly
- Check password matches the table above
- Try admin account first

### "Upload not working"
- Check file size (100 MB limit)
- Ensure you're logged in
- Check browser console for errors
- Try a simpler filename

### "Data looks wrong"
- Clear cache: `Ctrl+Shift+Delete` (browser)
- Reseed database: `python seed_db.py`
- Restart application: Stop and `python app.py`

---

## 📚 Documentation Files

- **README.md** - Main project documentation
- **MOCK_DATA_SUMMARY.md** - Detailed mock data info
- **PERSISTENCE.md** - Data persistence explanation
- **seed_db.py** - Database seeding script
- **database.py** - Database initialization

---

**You're all set! Start exploring the Smart DMS with complete mock data.** 🎉
