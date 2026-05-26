from werkzeug.security import generate_password_hash
from data.customers import (
    CUSTOMER_FILTERS as OFFICIAL_CUSTOMER_FILTERS,
    OFFICIAL_CUSTOMERS,
    normalize_customer_keys,
    normalize_customer_records,
)
from data.departments import (
    OFFICIAL_DEPARTMENT_MAP,
    OFFICIAL_DEPARTMENTS,
    normalize_department_keys,
    normalize_nested_department_keys,
    normalize_records,
    normalize_user_map,
)


USERS = {
    "diva@example.com": {
        "name": "Diva Chandra",
        "user_id": "U001",
        "emp_id": "EMP001",
        "email": "diva@example.com",
        "plant": "P1 - Trichy Plant",
        "department": "Quality",
        "password_hash": generate_password_hash("Pass@12345"),
        "role": "Admin",
    },
    "arun@example.com": {
        "name": "Arun Kumar",
        "user_id": "U014",
        "emp_id": "EMP014",
        "email": "arun@example.com",
        "plant": "P2 - Guduvachery Plant",
        "department": "Production",
        "password_hash": generate_password_hash("Prod@12345"),
        "role": "Manager",
    },
    "sneha@example.com": {
        "name": "Sneha Patel",
        "user_id": "U203",
        "emp_id": "EMP203",
        "email": "sneha@example.com",
        "plant": "P3 - Guduvachery Plant",
        "department": "Engineering",
        "password_hash": generate_password_hash("Eng@12345"),
        "role": "Approver",
    },
    "rahul@example.com": {
        "name": "Rahul Mehta",
        "user_id": "U089",
        "emp_id": "EMP089",
        "email": "rahul@example.com",
        "plant": "P4 - Uttarakhand Plant",
        "department": "Safety",
        "password_hash": generate_password_hash("Safe@12345"),
        "role": "User",
    },
    "vani@example.com": {
        "name": "Vani Raj",
        "user_id": "U117",
        "emp_id": "EMP117",
        "email": "vani@example.com",
        "plant": "P1 - Trichy Plant",
        "department": "Manufacturing",
        "password_hash": generate_password_hash("Mfg@12345"),
        "role": "Manager",
    },
    "karthik@example.com": {
        "name": "Karthik S",
        "user_id": "U055",
        "emp_id": "EMP055",
        "email": "karthik@example.com",
        "plant": "P2 - Guduvachery Plant",
        "department": "Maintenance",
        "password_hash": generate_password_hash("Maint@12345"),
        "role": "User",
    },
    "priya@example.com": {
        "name": "Priya Nair",
        "user_id": "U072",
        "emp_id": "EMP072",
        "email": "priya@example.com",
        "plant": "P4 - Uttarakhand Plant",
        "department": "Procurement",
        "password_hash": generate_password_hash("Proc@12345"),
        "role": "Approver",
    },
    "vikram@example.com": {
        "name": "Vikram Sharma",
        "user_id": "U102",
        "emp_id": "EMP102",
        "email": "vikram@example.com",
        "plant": "P1 - Trichy Plant",
        "department": "R&D",
        "password_hash": generate_password_hash("Rd@12345"),
        "role": "User",
    },
    "meera@example.com": {
        "name": "Meera Desai",
        "user_id": "U045",
        "emp_id": "EMP045",
        "email": "meera@example.com",
        "plant": "P3 - Guduvachery Plant",
        "department": "Operations",
        "password_hash": generate_password_hash("Ops@12345"),
        "role": "Manager",
    },
    "rajesh@example.com": {
        "name": "Rajesh Singh",
        "user_id": "U091",
        "emp_id": "EMP091",
        "email": "rajesh@example.com",
        "plant": "P2 - Guduvachery Plant",
        "department": "Stores",
        "password_hash": generate_password_hash("Stores@12345"),
        "role": "User",
    },
}


PLANTS = [
    {"id": "P1", "label": "P1 - Trichy Plant", "location": "Trichy, Tamil Nadu"},
    {"id": "P2", "label": "P2 - Guduvachery Plant", "location": "Guduvachery, Tamil Nadu"},
    {"id": "P3", "label": "P3 - Guduvachery Plant", "location": "Guduvachery, Tamil Nadu"},
    {"id": "P4", "label": "P4 - Uttarakhand Plant", "location": "Uttarakhand"},
]

MASTER_RECORD_PLANTS = [
    {"id": "P1", "label": "P1 - Trichy Plant", "location": "Trichy, Tamil Nadu"},
    {"id": "P2&3", "label": "P2&3 - Guduvachery Plants", "location": "Guduvachery, Tamil Nadu"},
    {"id": "P4", "label": "P4 - Uttarakhand Plant", "location": "Uttarakhand"},
]

CQA_DEPARTMENTS = dict(OFFICIAL_DEPARTMENT_MAP)


DEPARTMENTS = list(OFFICIAL_DEPARTMENTS)


CUSTOMER_RECORDS = {
    "AL - Ashok Leyland": [
        "ashok_shift_plan.xlsx",
        "ashok_work_order_report.pdf",
        "ashok_machine_tags.json",
        "ashok_machine_service_log.pdf",
        "ashok_breakdown_history.xlsx",
        "ashok_spares_list.csv",
    ],
    "TML - Tata Motors Limited": [
        "tata_design_revision_summary.pdf",
        "tata_component_drawing_pack.zip",
        "tata_bom_export.csv",
        "tata_dispatch_schedule.xlsx",
        "tata_process_instruction.pdf",
        "tata_capacity_plan.pptx",
    ],
    "M&M - Mahindra and Mahindra": [
        "hyundai_supplier_contract.pdf",
        "hyundai_material_specification.xlsx",
        "hyundai_price_revision.msg",
        "hyundai_quality_audit_report.pdf",
        "hyundai_ppap_checklist.docx",
        "hyundai_nc_summary.csv",
    ],
    "Switch Mobility": [
        "tvs_prototype_validation_report.pdf",
        "tvs_trial_run_results.xlsx",
        "tvs_sensor_dump.bin",
        "tvs_safety_compliance_certificate.pdf",
        "tvs_incident_prevention_plan.docx",
        "tvs_training_attendance.csv",
    ],
}


CUSTOMERS = list(OFFICIAL_CUSTOMERS)
CUSTOMER_FILTERS = list(OFFICIAL_CUSTOMER_FILTERS)


DASHBOARD_RECORDS = [
    {
        "id": 0,
        "name": "Diva Chandra",
        "user_id": "U001",
        "uploader_email": "diva@example.com",
        "plant": "P1 - Trichy Plant",
        "department": "Quality",
        "customer": "Internal",
        "file_name": "inspection_report_0420.pdf",
        "uploaded_at": "2026-04-20",
        "approval_status": "Approved",
    },
    {
        "id": 1,
        "name": "Arun Kumar",
        "user_id": "U014",
        "uploader_email": "arun@example.com",
        "plant": "P2 - Guduvachery Plant",
        "department": "Production",
        "customer": "Tata Motors",
        "file_name": "assembly_line_report.xlsx",
        "uploaded_at": "2026-04-19",
        "approval_status": "Pending",
    },
    {
        "id": 2,
        "name": "Sneha Patel",
        "user_id": "U203",
        "uploader_email": "sneha@example.com",
        "plant": "P3 - Guduvachery Plant",
        "department": "Engineering",
        "customer": "Hyundai Motors",
        "file_name": "cad_revision_summary.pdf",
        "uploaded_at": "2026-04-18",
        "approval_status": "Approved",
    },
    {
        "id": 3,
        "name": "Rahul Mehta",
        "user_id": "U089",
        "uploader_email": "rahul@example.com",
        "plant": "P4 - Uttarakhand Plant",
        "department": "Safety",
        "customer": "TVS Motors",
        "file_name": "safety_audit_report.pdf",
        "uploaded_at": "2026-04-17",
        "approval_status": "Rejected",
    },
    {
        "id": 4,
        "name": "Vani Raj",
        "user_id": "U117",
        "uploader_email": "vani@example.com",
        "plant": "P1 - Trichy Plant",
        "department": "Manufacturing",
        "customer": "Ashok Leyland",
        "file_name": "production_schedule_april.xlsx",
        "uploaded_at": "2026-04-16",
        "approval_status": "Pending",
    },
    {
        "id": 5,
        "name": "Karthik S",
        "user_id": "U055",
        "uploader_email": "karthik@example.com",
        "plant": "P2 - Guduvachery Plant",
        "department": "Maintenance",
        "customer": "Internal",
        "file_name": "preventive_maintenance_log.pdf",
        "uploaded_at": "2026-04-15",
        "approval_status": "Approved",
    },
    {
        "id": 6,
        "name": "Priya Nair",
        "user_id": "U072",
        "uploader_email": "priya@example.com",
        "plant": "P4 - Uttarakhand Plant",
        "department": "Procurement",
        "customer": "Tata Motors",
        "file_name": "vendor_contracts_q2.pdf",
        "uploaded_at": "2026-04-14",
        "approval_status": "Pending",
    },
]


ARCHIVE_RECORDS = [
    {
        "timestamp": "2026-04-20 08:32",
        "file_name": "inspection_report_q1.pdf",
        "plant": "P1 - Trichy Plant",
        "department": "Quality",
    },
    {
        "timestamp": "2026-04-19 17:04",
        "file_name": "line_status_legacy.xlsx",
        "plant": "P2 - Guduvachery Plant",
        "department": "Production",
    },
    {
        "timestamp": "2026-04-18 11:22",
        "file_name": "outdated_certificate.pdf",
        "plant": "P4 - Uttarakhand Plant",
        "department": "Safety",
    },
]


PLANT_ASSETS = {
    "P1 - Trichy Plant": {
        "Manufacturing": [
            "machine_layout_v2.pdf",
            "production_schedule_april.xlsx",
            "robot_program_backup.zip",
        ],
        "Quality": [
            "qa_checklist_rev3.docx",
            "inspection_report_0420.pdf",
            "gauge_calibration_log.csv",
        ],
        "Maintenance": [
            "compressor_service_log.pdf",
            "predictive_maintenance_sheet.xlsx",
            "motor_vibration_snapshot.png",
        ],
        "Safety": ["safety_induction_manual.pdf", "fire_drill_record.xlsx"],
    },
    "P2 - Guduvachery Plant": {
        "Production": [
            "assembly_line_report.pdf",
            "daily_shift_plan.xlsx",
            "line_balance_study.pptx",
        ],
        "Stores": [
            "inventory_sheet_q2.xlsx",
            "material_inward_log.pdf",
            "bin_card_backup.txt",
        ],
        "Maintenance": [
            "boiler_service_history.pdf",
            "spare_parts_catalogue.zip",
        ],
        "Engineering": ["p2_fixture_drawing.pdf", "p2_tooling_revision.xlsx"],
    },
    "P3 - Guduvachery Plant": {
        "R&D": [
            "prototype_notes.docx",
            "test_bench_results.pdf",
            "sensor_capture_data.json",
        ],
        "Engineering": [
            "cad_revision_summary.pdf",
            "tooling_plan.xlsx",
            "fixture_design.step",
        ],
        "Quality": [
            "validation_traceability_matrix.csv",
            "ppap_evidence_pack.zip",
        ],
        "Production": ["p3_shift_report.xlsx", "p3_cycle_time_study.pdf"],
    },
    "P4 - Uttarakhand Plant": {
        "Operations": [
            "ops_dashboard_extract.pdf",
            "shift_handover_notes.docx",
            "dispatch_matrix.xlsx",
        ],
        "Safety": [
            "safety_audit_report.pdf",
            "incident_matrix.xlsx",
            "ppe_compliance_photos.zip",
        ],
        "Procurement": [
            "vendor_rate_contracts.pdf",
            "purchase_plan_q3.xlsx",
        ],
        "Manufacturing": [
            "p4_production_log.pdf",
            "p4_machine_utilization.xlsx",
        ],
    },
}


SYSTEM_LOGS = [
    {
        "timestamp": "2026-04-20 10:30:15",
        "user_name": "Diva Chandra",
        "user_id": "U001",
        "action": "LOGIN",
        "details": "User logged in from 192.168.1.100",
    },
    {
        "timestamp": "2026-04-20 10:35:22",
        "user_name": "Diva Chandra",
        "user_id": "U001",
        "action": "DOCUMENT_UPLOAD",
        "details": "Uploaded: inspection_report_april_20.pdf to Quality",
    },
    {
        "timestamp": "2026-04-20 10:40:45",
        "user_name": "Sneha Patel",
        "user_id": "U203",
        "action": "DOCUMENT_APPROVED",
        "details": "Approved document: cad_revision_v5.pdf",
    },
    {
        "timestamp": "2026-04-20 11:15:30",
        "user_name": "Arun Kumar",
        "user_id": "U014",
        "action": "DOCUMENT_UPLOAD",
        "details": "Uploaded: assembly_line_daily_report.xlsx",
    },
    {
        "timestamp": "2026-04-20 11:45:00",
        "user_name": "Rahul Mehta",
        "user_id": "U089",
        "action": "DOCUMENT_REJECTED",
        "details": "Rejected: incident_investigation_report.pdf - Requires revision",
    },
    {
        "timestamp": "2026-04-20 14:22:10",
        "user_name": "Vani Raj",
        "user_id": "U117",
        "action": "DOCUMENT_UPLOAD",
        "details": "Uploaded: production_schedule_april.xlsx",
    },
    {
        "timestamp": "2026-04-20 15:30:45",
        "user_name": "Karthik S",
        "user_id": "U055",
        "action": "ARCHIVE_DOCUMENT",
        "details": "Archived: inspection_report_q1_2026.pdf",
    },
    {
        "timestamp": "2026-04-20 16:10:20",
        "user_name": "Priya Nair",
        "user_id": "U072",
        "action": "DOCUMENT_APPROVED",
        "details": "Approved: vendor_contracts_q2.pdf",
    },
    {
        "timestamp": "2026-04-20 16:45:50",
        "user_name": "Meera Desai",
        "user_id": "U045",
        "action": "LOGIN",
        "details": "User logged in from 192.168.1.108",
    },
    {
        "timestamp": "2026-04-20 17:20:15",
        "user_name": "Diva Chandra",
        "user_id": "U001",
        "action": "LOGOUT",
        "details": "User logged out",
    },
]


UPLOAD_LOGS = [
    {
        "timestamp": "2026-04-20 10:35:22",
        "user_name": "Diva Chandra",
        "user_id": "U001",
        "file_name": "inspection_report_april_20.pdf",
        "plant": "P1 - Trichy Plant",
        "department": "Quality",
        "status": "Success",
    },
    {
        "timestamp": "2026-04-20 11:15:30",
        "user_name": "Arun Kumar",
        "user_id": "U014",
        "file_name": "assembly_line_daily_report.xlsx",
        "plant": "P2 - Guduvachery Plant",
        "department": "Production",
        "status": "Success",
    },
    {
        "timestamp": "2026-04-20 14:22:10",
        "user_name": "Vani Raj",
        "user_id": "U117",
        "file_name": "production_schedule_april.xlsx",
        "plant": "P1 - Trichy Plant",
        "department": "Manufacturing",
        "status": "Success",
    },
]


USERS = normalize_user_map(USERS)
CUSTOMER_RECORDS = normalize_customer_keys(CUSTOMER_RECORDS)
DASHBOARD_RECORDS = normalize_customer_records(normalize_records(DASHBOARD_RECORDS))
ARCHIVE_RECORDS = normalize_customer_records(normalize_records(ARCHIVE_RECORDS))
PLANT_ASSETS = normalize_nested_department_keys(PLANT_ASSETS)
UPLOAD_LOGS = normalize_records(UPLOAD_LOGS)
