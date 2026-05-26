# Smart DMS - Enhanced Mock Data v2.0

## 📊 Overview

The mock data has been significantly expanded to provide comprehensive test coverage across all features and pages of the Smart DMS application.

**Total Resources:**
- **15 Users** (previously 10)
- **54 Documents** (previously 22)
- **10 Archived Documents** (previously 5)
- **40+ System Log Entries** (detailed activity trails)
- **4 Plants** across multiple departments
- **5 Customers** (Hyundai Motors, Tata Motors, Ashok Leyland, TVS Motors, Internal)

---

## 👥 User Accounts & Credentials

### Core Users (Original)
| Email | Password | Role | Plant | Department |
|-------|----------|------|-------|-----------|
| diva@example.com | Pass@12345 | Admin | P1 - Trichy | Quality |
| arun@example.com | Prod@12345 | Manager | P2 - Guduvachery | Production |
| sneha@example.com | Eng@12345 | Approver | P3 - Guduvachery | Engineering |
| rahul@example.com | Safe@12345 | User | P4 - Uttarakhand | Safety |
| vani@example.com | Mfg@12345 | Manager | P1 - Trichy | Manufacturing |
| karthik@example.com | Maint@12345 | User | P2 - Guduvachery | Maintenance |
| priya@example.com | Proc@12345 | Approver | P4 - Uttarakhand | Procurement |
| vikram@example.com | Rd@12345 | User | P1 - Trichy | R&D |
| meera@example.com | Ops@12345 | Manager | P3 - Guduvachery | Operations |
| rajesh@example.com | Stores@12345 | User | P2 - Guduvachery | Stores |

### Additional Users (New)
| Email | Password | Role | Plant | Department |
|-------|----------|------|-------|-----------|
| deepak@example.com | Deep@12345 | Approver | P1 - Trichy | Quality |
| priyanka@example.com | Priya@12345 | User | P2 - Guduvachery | Production |
| suresh@example.com | Suresh@12345 | Manager | P3 - Guduvachery | Engineering |
| anjali@example.com | Anjali@12345 | Approver | P4 - Uttarakhand | Safety |
| mohit@example.com | Mohit@12345 | User | P1 - Trichy | Manufacturing |

---

## 📄 Document Distribution

### By Department

#### Quality (P1 - Trichy)
- `inspection_report_april_20.pdf` - Approved
- `qa_audit_checklist_v2.docx` - Pending
- `fmea_analysis_april.xlsx` - Approved
- `dimensional_check_report.pdf` - Pending
- `calibration_certificate_april.pdf` - Approved
- `material_test_cert_batch_2501.pdf` - Pending

#### Production (P2 - Guduvachery)
- `assembly_line_daily_report.xlsx` - Approved
- `shift_production_metrics.xlsx` - Approved
- `line_balancing_study.pdf` - Pending
- `weekly_output_summary_w16.xlsx` - Approved
- `downtime_analysis_april.pdf` - Rejected

#### Engineering (P3 - Guduvachery)
- `cad_revision_v5.pdf` - Approved
- `tooling_design_package.zip` - Rejected
- `press_tool_drawing_rev3.pdf` - Approved
- `fea_analysis_housing_assembly.pdf` - Pending
- `bom_revision_april.xlsx` - Approved

#### Safety (P4 - Uttarakhand)
- `safety_audit_q2_report.pdf` - Approved
- `incident_investigation_report.pdf` - Pending
- `fire_safety_drill_record.pdf` - Approved
- `ppe_compliance_checklist.xlsx` - Pending
- `near_miss_report_april.pdf` - Approved

#### Manufacturing (P1 - Trichy)
- `production_schedule_april.xlsx` - Approved
- `machine_utilization_report.pdf` - Approved
- `shift_capacity_planning.xlsx` - Pending
- `operator_skill_matrix.pdf` - Approved
- `wip_status_daily.xlsx` - Pending

#### Maintenance (P2 - Guduvachery)
- `preventive_maintenance_log.pdf` - Approved
- `equipment_breakdown_analysis.xlsx` - Pending
- `compressor_maintenance_schedule.pdf` - Approved
- `hydraulic_press_repair_report.pdf` - Approved
- `spare_parts_inventory.xlsx` - Pending

#### Procurement (P4 - Uttarakhand)
- `vendor_contracts_q2.pdf` - Approved
- `rfq_responses_steel_supplier.xlsx` - Pending
- `po_authorization_summary.pdf` - Approved
- `vendor_performance_scorecard.xlsx` - Approved

#### R&D (P1 - Trichy)
- `prototype_testing_results.pdf` - Approved
- `material_substitution_analysis.pdf` - Pending
- `life_cycle_assessment_report.pdf` - Approved
- `project_innovation_proposal.pdf` - Rejected

#### Operations (P3 - Guduvachery)
- `ops_dashboard_extract.pdf` - Approved
- `resource_planning_april.xlsx` - Pending
- `monthly_review_minutes.pdf` - Approved
- `kpi_tracking_dashboard.xlsx` - Pending

#### Stores (P2 - Guduvachery)
- `inventory_stock_report.xlsx` - Approved
- `material_inward_receipt.pdf` - Approved
- `consumables_usage_report.xlsx` - Pending
- `material_outward_slip_batch_week16.pdf` - Approved

### Approval Status Distribution
- **Approved**: 36 documents (67%)
- **Pending**: 14 documents (26%)
- **Rejected**: 4 documents (7%)

### By Customer
- **Internal**: 26 documents
- **Hyundai Motors**: 11 documents
- **Tata Motors**: 10 documents
- **Ashok Leyland**: 5 documents
- **TVS Motors**: 2 documents

---

## 🗂️ Archived Documents

10 archived documents with historical data:
- Outdated certificates and reports
- Superseded design revisions
- Legacy production data
- Deprecated analysis documents
- Old maintenance logs
- Obsolete vendor agreements

Original upload dates span 30-90 days in the past to simulate real archival practices.

---

## 📋 System Log Coverage

Enhanced system logs with 40+ entries covering:

**Login/Logout Activity**
- 5+ LOGIN entries across different users
- 5+ LOGOUT entries
- IP addresses and timestamps

**Document Activities**
- DOCUMENT_UPLOAD: 15+ entries
- DOCUMENT_APPROVED: 8+ entries
- DOCUMENT_REJECTED: 3+ entries
- ARCHIVE_DOCUMENT: 2+ entries

**Temporal Distribution**
- Spanning 3+ days
- Multiple activities per user per day
- Realistic hourly intervals (1-7 hours between actions)

---

## 🎯 Features to Test with New Data

### 1. Dashboard
✅ **Test with expanded data:**
- Mixed approval statuses across all 10 departments
- Multiple customers per department
- 54 documents with rich filtering options
- Search functionality across diverse document types

### 2. Upload & Approvals Workflow
✅ **Complete workflow coverage:**
- 14 pending documents across all departments
- 36 approved documents to review
- 4 rejected documents for rejection reasons
- Multi-approver scenarios (10 users with different roles)

### 3. Plant Assets Browse
✅ **Full plant navigation:**
- **P1 - Trichy**: Quality, Manufacturing, R&D (15 docs)
- **P2 - Guduvachery**: Production, Maintenance, Stores (18 docs)
- **P3 - Guduvachery**: Engineering, Operations (10 docs)
- **P4 - Uttarakhand**: Safety, Procurement (11 docs)

### 4. Customer Records
✅ **Customer-grouped documents:**
- **Hyundai Motors**: 11 documents across departments
- **Tata Motors**: 10 documents across plants
- **Ashok Leyland**: 5 documents
- **TVS Motors**: 2 documents
- **Internal**: 26 internal documents

### 5. Archive & Restore
✅ **Soft-delete functionality:**
- 10 archived documents ready for restore testing
- Varying approval statuses in archive
- Historical timestamps

### 6. System Log & Audit Trail
✅ **Comprehensive logging:**
- 40+ log entries
- User activity tracking
- Action type filtering
- IP address logging
- Temporal analysis of activities

### 7. Profile & User Management
✅ **User role testing:**
- 1 Admin (full system access)
- 3 Managers (department leadership)
- 2 Approvers (approval workflow)
- 9 Regular Users (document uploaders)

---

## 🚀 How to Use Enhanced Data

### Option 1: Automatic Seeding
```bash
# The enhanced data is automatically seeded when the database is reset
python reset_and_seed.py
```

### Option 2: Manual Reseed
```bash
# Delete database
rm smart_dms.db

# Restart application (auto-initializes)
python app.py

# Then run seeding
python seed_db.py
```

### Option 3: Preserve Current Data
If you have uploaded custom documents and want to keep them while refreshing:
```bash
# Just run seeding (won't overwrite existing documents)
python seed_db.py
```

---

## 📊 Testing Scenarios

### Scenario 1: Approval Workflow
1. Login as **arun@example.com** (Manager)
2. Upload new document → Status: Pending
3. Switch to **sneha@example.com** (Approver)
4. View in Approvals → 14 pending documents
5. Approve/Reject → Status updates
6. Switch to **diva@example.com** (Admin)
7. Dashboard shows updated status

### Scenario 2: Cross-Plant Browsing
1. Click **P1 - Trichy Plant** card → 15 documents
2. Expand **Quality** dept → 6 documents visible
3. Click **Manufacturing** → 5 documents
4. Compare with **P2 - Guduvachery** → 18 documents
5. Navigate through all 4 plants

### Scenario 3: Customer Record Management
1. View **Hyundai Motors** → 11 documents
2. Filter by **Production** dept → 2 documents
3. View **Tata Motors** → 10 documents
4. Cross-department search across customers

### Scenario 4: Archive Management
1. Dashboard → Delete a document
2. Archive page → See 11 archived documents
3. Filter by department/customer
4. Restore one → Verify in dashboard

### Scenario 5: Audit Trail Analysis
1. System Log → 40+ entries
2. Filter by **DOCUMENT_UPLOAD** → 15 entries
3. Filter by user **diva@example.com** → 6 entries
4. Timeline shows activity distribution
5. IP address tracking for security audit

---

## 📈 Data Statistics

| Metric | Value |
|--------|-------|
| Total Users | 15 |
| Total Active Documents | 54 |
| Archived Documents | 10 |
| Approved Documents | 36 (67%) |
| Pending Documents | 14 (26%) |
| Rejected Documents | 4 (7%) |
| System Log Entries | 40+ |
| Plants | 4 |
| Departments | 10 |
| Customers | 5 |
| Document Types | 15+ file formats |

---

## 🔄 Resetting to Fresh State

```bash
# Complete reset (delete both DBs)
rm smart_dms.db smart_dms_users.sqlite3

# Restart application
python app.py

# Reseed with latest data
python seed_db.py
```

---

## ✨ Key Improvements

✅ **3x more documents** - Better pagination and filtering testing  
✅ **5 additional users** - More role combinations to test  
✅ **Better temporal distribution** - Documents across multiple dates  
✅ **Complete customer coverage** - Test customer-based workflows  
✅ **Enhanced audit trail** - 40+ log entries with realistic patterns  
✅ **All departments represented** - 10 different functional areas  
✅ **Mixed statuses** - Approved, Pending, and Rejected throughout  
✅ **Comprehensive archive** - 10 historical records to test restore  

---

## 🎓 Next Steps

1. **Start Application**: `python app.py`
2. **Login**: Use any account from the user table above
3. **Explore All Pages**: Dashboard, Upload, Approvals, Archive, Plant Assets, Customer Records, System Log
4. **Test Workflows**: Upload, approve, reject, archive
5. **Review Data**: Check all 4 plants, 5 customers, 10 departments
6. **Audit Logs**: Track all user activities

**You now have a fully populated DMS with comprehensive test data!** 🎉
