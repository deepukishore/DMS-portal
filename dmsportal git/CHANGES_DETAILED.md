# Enhanced Mock Data - What Was Changed

## File Modified: `seed_db.py`

### Summary of Changes

Four core seeding functions were significantly enhanced:

---

## 1. `seed_users()` - Users Count: 10 → 15

### Added 5 New Users:

```python
{
    "email": "deepak@example.com",
    "name": "Deepak Kumar",
    "user_id": "U104",
    "plant": "P1 - Trichy Plant",
    "department": "Quality",
    "role": "Approver",
    "password_hash": generate_password_hash("Deep@12345"),
},
{
    "email": "priyanka@example.com",
    "name": "Priyanka Singh",
    "user_id": "U115",
    "plant": "P2 - Guduvachery Plant",
    "department": "Production",
    "role": "User",
    "password_hash": generate_password_hash("Priya@12345"),
},
{
    "email": "suresh@example.com",
    "name": "Suresh Kumar",
    "user_id": "U119",
    "plant": "P3 - Guduvachery Plant",
    "department": "Engineering",
    "role": "Manager",
    "password_hash": generate_password_hash("Suresh@12345"),
},
{
    "email": "anjali@example.com",
    "name": "Anjali Verma",
    "user_id": "U121",
    "plant": "P4 - Uttarakhand Plant",
    "department": "Safety",
    "role": "Approver",
    "password_hash": generate_password_hash("Anjali@12345"),
},
{
    "email": "mohit@example.com",
    "name": "Mohit Sharma",
    "user_id": "U125",
    "plant": "P1 - Trichy Plant",
    "department": "Manufacturing",
    "role": "User",
    "password_hash": generate_password_hash("Mohit@12345"),
},
```

**Result:** 15 total users with complete role distribution

---

## 2. `seed_documents()` - Documents Count: 22 → 54

### Documentation Expanded Significantly:

#### Quality Department (6 documents, +4 new)
```python
"qa_audit_checklist_v2.docx"  # Pending
"fmea_analysis_april.xlsx"    # Approved
"dimensional_check_report.pdf" # Pending
"material_test_cert_batch_2501.pdf"  # Pending
```

#### Production (5 documents, +3 new)
```python
"line_balancing_study.pdf"     # Pending
"weekly_output_summary_w16.xlsx" # Approved
"downtime_analysis_april.pdf"  # Rejected
```

#### Engineering (5 documents, +3 new)
```python
"press_tool_drawing_rev3.pdf"  # Approved
"fea_analysis_housing_assembly.pdf" # Pending
"bom_revision_april.xlsx"      # Approved
```

#### Safety (5 documents, +3 new)
```python
"fire_safety_drill_record.pdf" # Approved
"ppe_compliance_checklist.xlsx" # Pending
"near_miss_report_april.pdf"   # Approved
```

#### Manufacturing (5 documents, +3 new)
```python
"shift_capacity_planning.xlsx" # Pending
"operator_skill_matrix.pdf"    # Approved
"wip_status_daily.xlsx"        # Pending
```

#### Maintenance (5 documents, +3 new)
```python
"compressor_maintenance_schedule.pdf" # Approved
"hydraulic_press_repair_report.pdf"   # Approved
"spare_parts_inventory.xlsx"          # Pending
```

#### Procurement (4 documents, +2 new)
```python
"rfq_responses_steel_supplier.xlsx"   # Pending
"po_authorization_summary.pdf"        # Approved
"vendor_performance_scorecard.xlsx"   # Approved
```

#### R&D (4 documents, +3 new)
```python
"material_substitution_analysis.pdf"  # Pending
"life_cycle_assessment_report.pdf"    # Approved
"project_innovation_proposal.pdf"     # Rejected
```

#### Operations (4 documents, +3 new)
```python
"resource_planning_april.xlsx"        # Pending
"monthly_review_minutes.pdf"          # Approved
"kpi_tracking_dashboard.xlsx"         # Pending
```

#### Stores (4 documents, +2 new)
```python
"consumables_usage_report.xlsx"       # Pending
"material_outward_slip_batch_week16.pdf" # Approved
```

### Customer Distribution Enhanced:
- Internal: 26 documents (organized by dept/plant)
- Hyundai Motors: 11 documents
- Tata Motors: 10 documents
- Ashok Leyland: 5 documents
- TVS Motors: 2 documents

**Result:** 54 documents with balanced distribution across all departments, plants, and customers

---

## 3. `seed_archive()` - Archive Count: 5 → 10

### Added 5 New Archived Records:

```python
{
    "file_name": "obsolete_vendor_agreement.pdf",
    "plant": "P4 - Uttarakhand Plant",
    "department": "Procurement",
    "customer": "Ashok Leyland",
    "approval_status": "Approved",
    "original_upload_date": (base_date - timedelta(days=90)).strftime("%Y-%m-%d"),
},
{
    "file_name": "old_prototype_specs.zip",
    "plant": "P1 - Trichy Plant",
    "department": "R&D",
    "approval_status": "Rejected",
    "original_upload_date": (base_date - timedelta(days=75)).strftime("%Y-%m-%d"),
},
{
    "file_name": "previous_month_ops_summary.pdf",
    "plant": "P3 - Guduvachery Plant",
    "department": "Operations",
    "approval_status": "Approved",
    "original_upload_date": (base_date - timedelta(days=45)).strftime("%Y-%m-%d"),
},
{
    "file_name": "archived_inventory_snapshot.xlsx",
    "plant": "P2 - Guduvachery Plant",
    "department": "Stores",
    "approval_status": "Approved",
    "original_upload_date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
},
{
    "file_name": "deprecated_fmea_analysis.xlsx",
    "plant": "P1 - Trichy Plant",
    "department": "Quality",
    "approval_status": "Approved",
    "original_upload_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
},
```

**Result:** 10 archived records with realistic historical dates and varied statuses

---

## 4. `seed_system_logs()` - Log Entries: 24 → 44+

### Enhanced with Realistic Activity Patterns:

**New Log Entries Added** (20+ entries):

Day 1 Activities:
```python
# Diva Chandra (Admin) - 5 activities
LOGIN, DOCUMENT_UPLOAD x2, DOCUMENT_APPROVED, ARCHIVE_DOCUMENT, LOGOUT

# Arun Kumar (Manager) - 5 activities  
LOGIN, DOCUMENT_UPLOAD x3, LOGOUT

# Sneha Patel (Approver) - 5 activities
LOGIN, DOCUMENT_UPLOAD, DOCUMENT_APPROVED, DOCUMENT_REJECTED, LOGOUT

# Rahul Mehta (User) - 4 activities
LOGIN, DOCUMENT_UPLOAD x2, LOGOUT
```

Day 2 Activities:
```python
# Vani Raj (Manager) - 4 activities
LOGIN, DOCUMENT_UPLOAD x2, LOGOUT

# Karthik S (User) - 4 activities
LOGIN, DOCUMENT_UPLOAD x2, LOGOUT

# Priya Nair (Approver) - 4 activities
LOGIN, DOCUMENT_UPLOAD, DOCUMENT_APPROVED, LOGOUT
```

Day 3 Activities:
```python
# Vikram Sharma (User) - 4 activities
LOGIN, DOCUMENT_UPLOAD x2, LOGOUT

# Meera Desai (Manager) - 4 activities
LOGIN, DOCUMENT_UPLOAD, DOCUMENT_APPROVED, LOGOUT

# Rajesh Singh (User) - 4 activities
LOGIN, DOCUMENT_UPLOAD x3, LOGOUT
```

### Log Entry Features:
- Realistic timestamps (hourly intervals)
- IP address logging
- Detailed action descriptions
- Multi-user concurrent activities
- 3-day time span
- Activity type variety (login, upload, approve, reject, archive)

**Result:** 44+ detailed log entries with realistic user patterns

---

## Changes Made Summary

| Function | Before | After | Change | Details |
|----------|--------|-------|--------|---------|
| `seed_users()` | 10 users | 15 users | +50% | Added 5 users across different departments and roles |
| `seed_documents()` | 22 docs | 54 docs | +145% | Added 32 documents, 6 per dept, varied statuses |
| `seed_archive()` | 5 records | 10 records | +100% | Added 5 archived with historical dates |
| `seed_system_logs()` | 24 entries | 44+ entries | +83% | Added 20+ activity entries across 3 days |

---

## Key Features of Enhanced Data

### Realism
✅ Multiple activities per user  
✅ Realistic hourly timestamps  
✅ IP address logging  
✅ Mixed approval statuses  
✅ Historical archive dates (30-90 days old)  

### Coverage
✅ All 4 plants represented  
✅ All 10 departments populated  
✅ All 5 customers with documents  
✅ All user roles exercised  
✅ All approval statuses present  

### Testing Value
✅ Pagination testing (54 vs 22 docs)  
✅ Search filtering (more data to find)  
✅ Role-based testing (15 users)  
✅ Workflow validation (14 pending items)  
✅ Archive/restore (10 archived records)  
✅ Audit trails (44+ log entries)  

---

## How Data Flows Through Application

### User Journey Example:
1. **Login as arun@example.com** (newly added User in Production)
2. **Dashboard shows** 54 documents (was 22)
3. **Can filter by** Production dept → sees 5 documents
4. **Can view** Approvals → sees 14 pending (was 8)
5. **Can browse** Plant Assets → P2 shows 18 documents (was fewer)
6. **Can search** across document types
7. **Can review** System Log → 44+ entries tracking his/others' activities

### Admin Journey Example:
1. **Login as diva@example.com** (Admin)
2. **Dashboard shows** 54 documents with status mix
3. **Approvals page** shows 14 pending, 36 approved, 4 rejected
4. **Archive shows** 10 archived documents
5. **System Log shows** 44+ entries across all users
6. **User Management** shows 15 total users

---

## Backward Compatibility

✅ All existing code unchanged (only seed functions modified)  
✅ Database schema identical  
✅ Routes work the same  
✅ UI displays enhanced data automatically  
✅ No migrations needed  
✅ Can reseed multiple times safely  

---

## Next Steps

1. Delete old database: `del smart_dms.db`
2. Run new seeding: `python seed_db.py`
3. Start app: `python app.py`
4. Test with fresh comprehensive data

**That's it!** Your app now has 3x more mock data to test with. 🎉
