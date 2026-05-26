# Smart DMS - Quick Reference Card

## 🚀 Start Application
```bash
python app.py
# Open: http://localhost:5000
```

## 🔐 Demo Login (Recommended)
```
Email: diva@example.com
Password: Pass@12345
Role: Admin
```

---

## 📊 Current Mock Data

```
Users:        10 (1 Admin, 3 Managers, 2 Approvers, 4 Users)
Documents:    22 (12 Approved, 8 Pending, 2 Rejected)
Archives:      5 (Soft-deleted documents)
System Logs:  24 (Login, Upload, Approval activities)
Plants:        4 (Trichy, Guduvachery x2, Uttarakhand)
Departments:  10+ (Quality, Production, Engineering, etc.)
Customers:     5 (Hyundai, Tata, Ashok Leyland, TVS, Internal)
```

---

## 👥 Key Demo Users

| Role | Email | Password | Plant |
|------|-------|----------|-------|
| **Admin** | diva@example.com | Pass@12345 | P1 |
| **Manager** | arun@example.com | Prod@12345 | P2 |
| **Approver** | sneha@example.com | Eng@12345 | P3 |
| **User** | rahul@example.com | Safe@12345 | P4 |

*(See MOCK_DATA_QUICK_START.md for all 10 users)*

---

## 🎯 Feature Test Checklist

- [ ] Login & Dashboard (see mixed document statuses)
- [ ] Search & Filter (by plant, department, status)
- [ ] Upload (new document → auto-pending)
- [ ] Approvals (approve/reject pending docs)
- [ ] Plant Assets (browse by plant → department)
- [ ] Customer Records (view by customer)
- [ ] Archive (delete → restore workflow)
- [ ] System Logs (view activity timeline)
- [ ] Profile (view user details)

---

## 🔄 Common Tasks

### Approve a Document
1. Login as Admin (diva@example.com)
2. Go to "Approvals" page
3. Click "Approve" on any Pending document
4. Status updates immediately

### Upload New Document
1. Go to "Upload" page
2. Drag & drop or click to select file
3. Fill in Plant, Department, Customer
4. Click "Upload" → Document appears in Dashboard (Pending)

### View Plant Assets
1. Go to "Plant Assets" page
2. Click any plant card
3. Select department tab
4. View documents in that department

### Delete & Restore
1. Dashboard → Click "Delete" on any document
2. Document moves to "Archive" page
3. Click "Restore" → Returns to Dashboard

### Search Documents
1. Dashboard → Search box at top
2. Type filename or partial name
3. Results filter in real-time

---

## 📁 File Structure

```
dms_portal_test/
├── app.py                           # Main app
├── database.py                      # DB setup
├── seed_db.py                       # Mock data script
├── smart_dms.db                     # SQLite database
│
├── routes/                          # Page handlers
│   ├── dashboard_routes.py
│   ├── upload_routes.py
│   ├── approval_routes.py
│   ├── archive_routes.py
│   ├── plant_assets_routes.py
│   ├── customer_records_routes.py
│   ├── system_log_routes.py
│   └── auth_routes.py
│
├── services/                        # Business logic
│   ├── document_service.py
│   ├── auth_service.py
│   └── ...
│
├── templates/                       # HTML pages
│   ├── dashboard.html
│   ├── upload.html
│   ├── approvals.html
│   ├── archive.html
│   ├── plant_assets.html
│   ├── customer_records.html
│   ├── system_log.html
│   └── auth/
│       ├── login.html
│       └── register.html
│
├── static/                          # CSS & JS
│   ├── css/app.css
│   └── js/upload.js
│
└── uploads/                         # Uploaded files
```

---

## 🗂️ Document States

| Status | Description | Count |
|--------|-------------|-------|
| Approved ✅ | Ready for use | 12 |
| Pending ⏳ | Awaiting approval | 8 |
| Rejected ❌ | Not accepted | 2 |
| Archived 📦 | Soft-deleted | 5 |

---

## 🌍 Plants

| ID | Name | Location |
|----|------|----------|
| P1 | Trichy Plant | Trichy, Tamil Nadu |
| P2 | Guduvachery Plant | Guduvachery, Tamil Nadu |
| P3 | Guduvachery Plant | Guduvachery, Tamil Nadu |
| P4 | Uttarakhand Plant | Uttarakhand |

---

## 🏭 Departments

Quality • Production • Engineering • Manufacturing • Maintenance • R&D • Safety • Procurement • Operations • Stores

---

## 🤝 Customers

- Hyundai Motors
- Tata Motors
- Ashok Leyland
- TVS Motors
- Internal

---

## 🔧 Database Reset

### Full Reset (Delete All)
```bash
rm smart_dms.db
python app.py  # Creates fresh DB
```

### Reseed Mock Data
```bash
python seed_db.py  # Adds mock data (won't duplicate)
```

### Reset & Reseed
```bash
rm smart_dms.db
python seed_db.py
python app.py
```

---

## 💾 Database Tables

1. **users** - 10 demo accounts
2. **documents** - 22 sample docs
3. **archive** - 5 archived docs
4. **system_logs** - 24 activity entries
5. **category_documents** - Categorized docs
6. **revision_history** - Document versions
7. **document_versions** - Version tracking

---

## 📝 Sample Document Names

```
inspection_report_april_20.pdf
qa_audit_checklist.docx
assembly_line_daily_report.xlsx
shift_production_metrics.xlsx
cad_revision_v5.pdf
tooling_design_package.zip
safety_audit_q2_report.pdf
preventive_maintenance_log.pdf
prototype_testing_results.pdf
vendor_contracts_q2.pdf
```

---

## 🆘 Quick Fixes

| Issue | Fix |
|-------|-----|
| No documents showing | Refresh page, check filters |
| Login fails | Verify email & password |
| Upload fails | Check file size (<100MB) |
| Data looks stale | Reseed: `python seed_db.py` |
| App won't start | Delete `smart_dms.db`, run `python app.py` |

---

## 📞 Support Docs

- **README.md** - Full project info
- **MOCK_DATA_QUICK_START.md** - Detailed guide
- **MOCK_DATA_SUMMARY.md** - Data overview
- **PERSISTENCE.md** - How data persists

---

**Created**: Mock data fully seeded and ready to use! 🎉
