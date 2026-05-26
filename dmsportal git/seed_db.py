"""
Database seeding script to populate the Smart DMS with comprehensive mock data.
This script creates sample users, documents, archives, and system logs to showcase all features.

Run this script after initializing the database:
    python seed_db.py
"""
from datetime import datetime, timedelta
import sqlite3
from data.customers import normalize_customer_records
from data.departments import normalize_records
from werkzeug.security import generate_password_hash
from database import get_connection

def seed_users():
    """Create sample users with different roles and departments."""
    users = [
        {
            "email": "diva@example.com",
            "name": "Diva Chandra",
            "user_id": "U001",
            "emp_id": "EMP001",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "password_hash": generate_password_hash("Pass@12345"),
            "role": "Admin",
        },
        {
            "email": "arun@example.com",
            "name": "Arun Kumar",
            "user_id": "U014",
            "emp_id": "EMP014",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "password_hash": generate_password_hash("Prod@12345"),
            "role": "Manager",
        },
        {
            "email": "sneha@example.com",
            "name": "Sneha Patel",
            "user_id": "U203",
            "emp_id": "EMP203",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "password_hash": generate_password_hash("Eng@12345"),
            "role": "Approver",
        },
        {
            "email": "rahul@example.com",
            "name": "Rahul Mehta",
            "user_id": "U089",
            "emp_id": "EMP089",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "password_hash": generate_password_hash("Safe@12345"),
            "role": "User",
        },
        {
            "email": "vani@example.com",
            "name": "Vani Raj",
            "user_id": "U117",
            "emp_id": "EMP117",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "password_hash": generate_password_hash("Mfg@12345"),
            "role": "Manager",
        },
        {
            "email": "karthik@example.com",
            "name": "Karthik S",
            "user_id": "U055",
            "emp_id": "EMP055",
            "plant": "P2 - Guduvachery Plant",
            "department": "Maintenance",
            "password_hash": generate_password_hash("Maint@12345"),
            "role": "User",
        },
        {
            "email": "priya@example.com",
            "name": "Priya Nair",
            "user_id": "U072",
            "emp_id": "EMP072",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Procurement",
            "password_hash": generate_password_hash("Proc@12345"),
            "role": "Approver",
        },
        {
            "email": "vikram@example.com",
            "name": "Vikram Sharma",
            "user_id": "U102",
            "emp_id": "EMP102",
            "plant": "P1 - Trichy Plant",
            "department": "R&D",
            "password_hash": generate_password_hash("Rd@12345"),
            "role": "User",
        },
        {
            "email": "meera@example.com",
            "name": "Meera Desai",
            "user_id": "U045",
            "emp_id": "EMP045",
            "plant": "P3 - Guduvachery Plant",
            "department": "Operations",
            "password_hash": generate_password_hash("Ops@12345"),
            "role": "Manager",
        },
        {
            "email": "rajesh@example.com",
            "name": "Rajesh Singh",
            "user_id": "U091",
            "emp_id": "EMP091",
            "plant": "P2 - Guduvachery Plant",
            "department": "Stores",
            "password_hash": generate_password_hash("Stores@12345"),
            "role": "User",
        },
        # Additional users for better coverage
        {
            "email": "deepak@example.com",
            "name": "Deepak Kumar",
            "user_id": "U104",
            "emp_id": "EMP104",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "password_hash": generate_password_hash("Deep@12345"),
            "role": "Approver",
        },
        {
            "email": "priyanka@example.com",
            "name": "Priyanka Singh",
            "user_id": "U115",
            "emp_id": "EMP115",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "password_hash": generate_password_hash("Priya@12345"),
            "role": "User",
        },
        {
            "email": "suresh@example.com",
            "name": "Suresh Kumar",
            "user_id": "U119",
            "emp_id": "EMP119",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "password_hash": generate_password_hash("Suresh@12345"),
            "role": "Manager",
        },
        {
            "email": "anjali@example.com",
            "name": "Anjali Verma",
            "user_id": "U121",
            "emp_id": "EMP121",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "password_hash": generate_password_hash("Anjali@12345"),
            "role": "Approver",
        },
        {
            "email": "mohit@example.com",
            "name": "Mohit Sharma",
            "user_id": "U125",
            "emp_id": "EMP125",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "password_hash": generate_password_hash("Mohit@12345"),
            "role": "User",
        },
    ]
    users = normalize_records(users)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for user in users:
        cursor.execute(
            'SELECT email FROM users WHERE email = ?',
            (user['email'],)
        )
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (email, name, user_id, emp_id, plant, department, password_hash, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user['email'], user['name'], user['user_id'], user['emp_id'], 
                  user['plant'], user['department'], user['password_hash'], user['role']))
            print(f"[+] Created user: {user['name']} ({user['email']})")
    
    conn.commit()
    conn.close()


def seed_documents():
    """Create sample documents with various statuses and departments."""
    base_date = datetime(2026, 4, 1)
    documents = [
        # ========== TRICHY PLANT (P1) - QUALITY ==========
        {
            "name": "Diva Chandra",
            "user_id": "U001",
            "uploader_email": "diva@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Internal",
            "file_name": "inspection_report_april_20.pdf",
            "uploaded_at": (base_date + timedelta(days=19)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=18)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Diva Chandra",
            "user_id": "U001",
            "uploader_email": "diva@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Hyundai Motors",
            "file_name": "qa_audit_checklist_v2.docx",
            "uploaded_at": (base_date + timedelta(days=18)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Diva Chandra",
            "user_id": "U001",
            "uploader_email": "diva@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Tata Motors",
            "file_name": "fmea_analysis_april.xlsx",
            "uploaded_at": (base_date + timedelta(days=17)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=16)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Diva Chandra",
            "user_id": "U001",
            "uploader_email": "diva@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Ashok Leyland",
            "file_name": "dimensional_check_report.pdf",
            "uploaded_at": (base_date + timedelta(days=16)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Diva Chandra",
            "user_id": "U001",
            "uploader_email": "diva@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Internal",
            "file_name": "calibration_certificate_april.pdf",
            "uploaded_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Diva Chandra",
            "user_id": "U001",
            "uploader_email": "diva@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "TVS Motors",
            "file_name": "material_test_cert_batch_2501.pdf",
            "uploaded_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        # ========== GUDUVACHERY P2 - PRODUCTION ==========
        {
            "name": "Arun Kumar",
            "user_id": "U014",
            "uploader_email": "arun@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "customer": "Tata Motors",
            "file_name": "assembly_line_daily_report.xlsx",
            "uploaded_at": (base_date + timedelta(days=17)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=17)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Arun Kumar",
            "user_id": "U014",
            "uploader_email": "arun@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "customer": "Internal",
            "file_name": "shift_production_metrics.xlsx",
            "uploaded_at": (base_date + timedelta(days=16)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=15)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Arun Kumar",
            "user_id": "U014",
            "uploader_email": "arun@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "customer": "Ashok Leyland",
            "file_name": "line_balancing_study.pdf",
            "uploaded_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Arun Kumar",
            "user_id": "U014",
            "uploader_email": "arun@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "customer": "Hyundai Motors",
            "file_name": "weekly_output_summary_w16.xlsx",
            "uploaded_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Arun Kumar",
            "user_id": "U014",
            "uploader_email": "arun@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "customer": "Internal",
            "file_name": "downtime_analysis_april.pdf",
            "uploaded_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "approval_status": "Rejected",
            "approval_updated_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        # ========== GUDUVACHERY P3 - ENGINEERING ==========
        {
            "name": "Sneha Patel",
            "user_id": "U203",
            "uploader_email": "sneha@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "customer": "Hyundai Motors",
            "file_name": "cad_revision_v5.pdf",
            "uploaded_at": (base_date + timedelta(days=15)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=14)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Sneha Patel",
            "user_id": "U203",
            "uploader_email": "sneha@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "customer": "Internal",
            "file_name": "tooling_design_package.zip",
            "uploaded_at": (base_date + timedelta(days=14)).strftime("%Y-%m-%d"),
            "approval_status": "Rejected",
            "approval_updated_at": (base_date + timedelta(days=13)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Sneha Patel",
            "user_id": "U203",
            "uploader_email": "sneha@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "customer": "Tata Motors",
            "file_name": "press_tool_drawing_rev3.pdf",
            "uploaded_at": (base_date + timedelta(days=12)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=11)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Sneha Patel",
            "user_id": "U203",
            "uploader_email": "sneha@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "customer": "Internal",
            "file_name": "fea_analysis_housing_assembly.pdf",
            "uploaded_at": (base_date + timedelta(days=8)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Sneha Patel",
            "user_id": "U203",
            "uploader_email": "sneha@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "customer": "Ashok Leyland",
            "file_name": "bom_revision_april.xlsx",
            "uploaded_at": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
        },
        # ========== UTTARAKHAND PLANT (P4) - SAFETY ==========
        {
            "name": "Rahul Mehta",
            "user_id": "U089",
            "uploader_email": "rahul@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "customer": "TVS Motors",
            "file_name": "safety_audit_q2_report.pdf",
            "uploaded_at": (base_date + timedelta(days=13)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=12)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Rahul Mehta",
            "user_id": "U089",
            "uploader_email": "rahul@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "customer": "Internal",
            "file_name": "incident_investigation_report.pdf",
            "uploaded_at": (base_date + timedelta(days=12)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Rahul Mehta",
            "user_id": "U089",
            "uploader_email": "rahul@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "customer": "Hyundai Motors",
            "file_name": "fire_safety_drill_record.pdf",
            "uploaded_at": (base_date + timedelta(days=10)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=9)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Rahul Mehta",
            "user_id": "U089",
            "uploader_email": "rahul@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "customer": "Internal",
            "file_name": "ppe_compliance_checklist.xlsx",
            "uploaded_at": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Rahul Mehta",
            "user_id": "U089",
            "uploader_email": "rahul@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "customer": "Tata Motors",
            "file_name": "near_miss_report_april.pdf",
            "uploaded_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        # ========== TRICHY PLANT (P1) - MANUFACTURING ==========
        {
            "name": "Vani Raj",
            "user_id": "U117",
            "uploader_email": "vani@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "customer": "Ashok Leyland",
            "file_name": "production_schedule_april.xlsx",
            "uploaded_at": (base_date + timedelta(days=11)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=10)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Vani Raj",
            "user_id": "U117",
            "uploader_email": "vani@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "customer": "Internal",
            "file_name": "machine_utilization_report.pdf",
            "uploaded_at": (base_date + timedelta(days=10)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=9)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Vani Raj",
            "user_id": "U117",
            "uploader_email": "vani@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "customer": "Hyundai Motors",
            "file_name": "shift_capacity_planning.xlsx",
            "uploaded_at": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Vani Raj",
            "user_id": "U117",
            "uploader_email": "vani@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "customer": "TVS Motors",
            "file_name": "operator_skill_matrix.pdf",
            "uploaded_at": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Vani Raj",
            "user_id": "U117",
            "uploader_email": "vani@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "Manufacturing",
            "customer": "Internal",
            "file_name": "wip_status_daily.xlsx",
            "uploaded_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        # ========== GUDUVACHERY P2 - MAINTENANCE ==========
        {
            "name": "Karthik S",
            "user_id": "U055",
            "uploader_email": "karthik@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Maintenance",
            "customer": "Internal",
            "file_name": "preventive_maintenance_log.pdf",
            "uploaded_at": (base_date + timedelta(days=9)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=8)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Karthik S",
            "user_id": "U055",
            "uploader_email": "karthik@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Maintenance",
            "customer": "Internal",
            "file_name": "equipment_breakdown_analysis.xlsx",
            "uploaded_at": (base_date + timedelta(days=8)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Karthik S",
            "user_id": "U055",
            "uploader_email": "karthik@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Maintenance",
            "customer": "Hyundai Motors",
            "file_name": "compressor_maintenance_schedule.pdf",
            "uploaded_at": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Karthik S",
            "user_id": "U055",
            "uploader_email": "karthik@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Maintenance",
            "customer": "Tata Motors",
            "file_name": "hydraulic_press_repair_report.pdf",
            "uploaded_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Karthik S",
            "user_id": "U055",
            "uploader_email": "karthik@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Maintenance",
            "customer": "Internal",
            "file_name": "spare_parts_inventory.xlsx",
            "uploaded_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        # ========== UTTARAKHAND PLANT (P4) - PROCUREMENT ==========
        {
            "name": "Priya Nair",
            "user_id": "U072",
            "uploader_email": "priya@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Procurement",
            "customer": "Tata Motors",
            "file_name": "vendor_contracts_q2.pdf",
            "uploaded_at": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Priya Nair",
            "user_id": "U072",
            "uploader_email": "priya@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Procurement",
            "customer": "Hyundai Motors",
            "file_name": "rfq_responses_steel_supplier.xlsx",
            "uploaded_at": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Priya Nair",
            "user_id": "U072",
            "uploader_email": "priya@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Procurement",
            "customer": "Internal",
            "file_name": "po_authorization_summary.pdf",
            "uploaded_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Priya Nair",
            "user_id": "U072",
            "uploader_email": "priya@example.com",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Procurement",
            "customer": "Ashok Leyland",
            "file_name": "vendor_performance_scorecard.xlsx",
            "uploaded_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        # ========== TRICHY PLANT (P1) - R&D ==========
        {
            "name": "Vikram Sharma",
            "user_id": "U102",
            "uploader_email": "vikram@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "R&D",
            "customer": "Internal",
            "file_name": "prototype_testing_results.pdf",
            "uploaded_at": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Vikram Sharma",
            "user_id": "U102",
            "uploader_email": "vikram@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "R&D",
            "customer": "Hyundai Motors",
            "file_name": "material_substitution_analysis.pdf",
            "uploaded_at": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Vikram Sharma",
            "user_id": "U102",
            "uploader_email": "vikram@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "R&D",
            "customer": "Tata Motors",
            "file_name": "life_cycle_assessment_report.pdf",
            "uploaded_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Vikram Sharma",
            "user_id": "U102",
            "uploader_email": "vikram@example.com",
            "plant": "P1 - Trichy Plant",
            "department": "R&D",
            "customer": "Internal",
            "file_name": "project_innovation_proposal.pdf",
            "uploaded_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "approval_status": "Rejected",
            "approval_updated_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        # ========== GUDUVACHERY P3 - OPERATIONS ==========
        {
            "name": "Meera Desai",
            "user_id": "U045",
            "uploader_email": "meera@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Operations",
            "customer": "Internal",
            "file_name": "ops_dashboard_extract.pdf",
            "uploaded_at": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Meera Desai",
            "user_id": "U045",
            "uploader_email": "meera@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Operations",
            "customer": "Ashok Leyland",
            "file_name": "resource_planning_april.xlsx",
            "uploaded_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Meera Desai",
            "user_id": "U045",
            "uploader_email": "meera@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Operations",
            "customer": "TVS Motors",
            "file_name": "monthly_review_minutes.pdf",
            "uploaded_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Meera Desai",
            "user_id": "U045",
            "uploader_email": "meera@example.com",
            "plant": "P3 - Guduvachery Plant",
            "department": "Operations",
            "customer": "Internal",
            "file_name": "kpi_tracking_dashboard.xlsx",
            "uploaded_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        # ========== GUDUVACHERY P2 - STORES ==========
        {
            "name": "Rajesh Singh",
            "user_id": "U091",
            "uploader_email": "rajesh@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Stores",
            "customer": "Internal",
            "file_name": "inventory_stock_report.xlsx",
            "uploaded_at": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Rajesh Singh",
            "user_id": "U091",
            "uploader_email": "rajesh@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Stores",
            "customer": "Internal",
            "file_name": "material_inward_receipt.pdf",
            "uploaded_at": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        {
            "name": "Rajesh Singh",
            "user_id": "U091",
            "uploader_email": "rajesh@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Stores",
            "customer": "Hyundai Motors",
            "file_name": "consumables_usage_report.xlsx",
            "uploaded_at": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "approval_status": "Pending",
            "approval_updated_at": None,
        },
        {
            "name": "Rajesh Singh",
            "user_id": "U091",
            "uploader_email": "rajesh@example.com",
            "plant": "P2 - Guduvachery Plant",
            "department": "Stores",
            "customer": "Tata Motors",
            "file_name": "material_outward_slip_batch_week16.pdf",
            "uploaded_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "approval_status": "Approved",
            "approval_updated_at": (base_date + timedelta(days=0)).strftime("%Y-%m-%d"),
        },
    ]
    documents = normalize_customer_records(normalize_records(documents))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        cursor.execute(
            'SELECT id FROM documents WHERE file_name = ?',
            (doc['file_name'],)
        )
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO documents 
                (name, user_id, uploader_email, plant, department, customer, file_name, uploaded_at, approval_status, approval_updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (doc['name'], doc['user_id'], doc['uploader_email'], doc['plant'],
                  doc['department'], doc['customer'], doc['file_name'], doc['uploaded_at'],
                  doc['approval_status'], doc['approval_updated_at']))
            print(f"[+] Created document: {doc['file_name']} - Status: {doc['approval_status']}")
    
    conn.commit()
    conn.close()


def seed_archive():
    """Create sample archived documents."""
    base_date = datetime(2026, 3, 1)
    archive_records = [
        {
            "timestamp": (base_date + timedelta(days=30)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "inspection_report_q1_2026.pdf",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Internal",
            "uploaded_by": "Diva Chandra",
            "user_id": "U001",
            "approval_status": "Approved",
            "original_upload_date": (base_date + timedelta(days=15)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=25)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "legacy_production_data.xlsx",
            "plant": "P2 - Guduvachery Plant",
            "department": "Production",
            "customer": "Tata Motors",
            "uploaded_by": "Arun Kumar",
            "user_id": "U014",
            "approval_status": "Approved",
            "original_upload_date": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=20)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "outdated_certificate.pdf",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Safety",
            "customer": "Internal",
            "uploaded_by": "Rahul Mehta",
            "user_id": "U089",
            "approval_status": "Approved",
            "original_upload_date": (base_date - timedelta(days=45)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=15)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "superseded_design_revision.pdf",
            "plant": "P3 - Guduvachery Plant",
            "department": "Engineering",
            "customer": "Hyundai Motors",
            "uploaded_by": "Sneha Patel",
            "user_id": "U203",
            "approval_status": "Rejected",
            "original_upload_date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=10)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "old_maintenance_log.pdf",
            "plant": "P1 - Trichy Plant",
            "department": "Maintenance",
            "customer": "Internal",
            "uploaded_by": "Karthik S",
            "user_id": "U055",
            "approval_status": "Approved",
            "original_upload_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=5)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "obsolete_vendor_agreement.pdf",
            "plant": "P4 - Uttarakhand Plant",
            "department": "Procurement",
            "customer": "Ashok Leyland",
            "uploaded_by": "Priya Nair",
            "user_id": "U072",
            "approval_status": "Approved",
            "original_upload_date": (base_date - timedelta(days=90)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=8)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "old_prototype_specs.zip",
            "plant": "P1 - Trichy Plant",
            "department": "R&D",
            "customer": "Internal",
            "uploaded_by": "Vikram Sharma",
            "user_id": "U102",
            "approval_status": "Rejected",
            "original_upload_date": (base_date - timedelta(days=75)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "previous_month_ops_summary.pdf",
            "plant": "P3 - Guduvachery Plant",
            "department": "Operations",
            "customer": "TVS Motors",
            "uploaded_by": "Meera Desai",
            "user_id": "U045",
            "approval_status": "Approved",
            "original_upload_date": (base_date - timedelta(days=45)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=12)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "archived_inventory_snapshot.xlsx",
            "plant": "P2 - Guduvachery Plant",
            "department": "Stores",
            "customer": "Internal",
            "uploaded_by": "Rajesh Singh",
            "user_id": "U091",
            "approval_status": "Approved",
            "original_upload_date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
        },
        {
            "timestamp": (base_date + timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "file_name": "deprecated_fmea_analysis.xlsx",
            "plant": "P1 - Trichy Plant",
            "department": "Quality",
            "customer": "Hyundai Motors",
            "uploaded_by": "Diva Chandra",
            "user_id": "U001",
            "approval_status": "Approved",
            "original_upload_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
    ]
    archive_records = normalize_customer_records(normalize_records(archive_records))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for rec in archive_records:
        cursor.execute(
            'SELECT id FROM archive WHERE file_name = ?',
            (rec['file_name'],)
        )
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO archive 
                (timestamp, file_name, plant, department, customer, uploaded_by, user_id, approval_status, original_upload_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (rec['timestamp'], rec['file_name'], rec['plant'], rec['department'],
                  rec['customer'], rec['uploaded_by'], rec['user_id'], rec['approval_status'],
                  rec['original_upload_date']))
            print(f"[+] Archived document: {rec['file_name']}")
    
    conn.commit()
    conn.close()


def seed_system_logs():
    """Create sample system logs showing various activities."""
    base_date = datetime.now() - timedelta(days=10)
    system_logs = [
        # Day 1 - Diva (Admin)
        {
            "timestamp": (base_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Diva Chandra",
            "user_id": "U001",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.100",
        },
        {
            "timestamp": (base_date + timedelta(hours=1, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Diva Chandra",
            "user_id": "U001",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: inspection_report_april_20.pdf (Quality, P1)",
        },
        {
            "timestamp": (base_date + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Diva Chandra",
            "user_id": "U001",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: fmea_analysis_april.xlsx (Quality, P1)",
        },
        {
            "timestamp": (base_date + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Diva Chandra",
            "user_id": "U001",
            "action": "DOCUMENT_APPROVED",
            "details": "Approved: qa_audit_checklist_v2.docx",
        },
        {
            "timestamp": (base_date + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Diva Chandra",
            "user_id": "U001",
            "action": "ARCHIVE_DOCUMENT",
            "details": "Archived: inspection_report_q1_2026.pdf",
        },
        {
            "timestamp": (base_date + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Diva Chandra",
            "user_id": "U001",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 1 - Arun (Manager, Production)
        {
            "timestamp": (base_date + timedelta(hours=2, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Arun Kumar",
            "user_id": "U014",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.102",
        },
        {
            "timestamp": (base_date + timedelta(hours=2, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Arun Kumar",
            "user_id": "U014",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: assembly_line_daily_report.xlsx (Production, P2)",
        },
        {
            "timestamp": (base_date + timedelta(hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Arun Kumar",
            "user_id": "U014",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: shift_production_metrics.xlsx (Production, P2)",
        },
        {
            "timestamp": (base_date + timedelta(hours=5, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Arun Kumar",
            "user_id": "U014",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: line_balancing_study.pdf (Production, P2)",
        },
        {
            "timestamp": (base_date + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Arun Kumar",
            "user_id": "U014",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 1 - Sneha (Approver, Engineering)
        {
            "timestamp": (base_date + timedelta(hours=3, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Sneha Patel",
            "user_id": "U203",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.103",
        },
        {
            "timestamp": (base_date + timedelta(hours=4, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Sneha Patel",
            "user_id": "U203",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: cad_revision_v5.pdf (Engineering, P3)",
        },
        {
            "timestamp": (base_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Sneha Patel",
            "user_id": "U203",
            "action": "DOCUMENT_APPROVED",
            "details": "Approved: cad_revision_v5.pdf",
        },
        {
            "timestamp": (base_date + timedelta(hours=6, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Sneha Patel",
            "user_id": "U203",
            "action": "DOCUMENT_REJECTED",
            "details": "Rejected: tooling_design_package.zip - Needs QA review",
        },
        {
            "timestamp": (base_date + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Sneha Patel",
            "user_id": "U203",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 1 - Rahul (User, Safety)
        {
            "timestamp": (base_date + timedelta(hours=4, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rahul Mehta",
            "user_id": "U089",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.104",
        },
        {
            "timestamp": (base_date + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rahul Mehta",
            "user_id": "U089",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: safety_audit_q2_report.pdf (Safety, P4)",
        },
        {
            "timestamp": (base_date + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rahul Mehta",
            "user_id": "U089",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: incident_investigation_report.pdf (Safety, P4)",
        },
        {
            "timestamp": (base_date + timedelta(hours=7, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rahul Mehta",
            "user_id": "U089",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 2 - Vani (Manager, Manufacturing)
        {
            "timestamp": (base_date + timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vani Raj",
            "user_id": "U117",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.101",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=1, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vani Raj",
            "user_id": "U117",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: production_schedule_april.xlsx (Manufacturing, P1)",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=2, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vani Raj",
            "user_id": "U117",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: machine_utilization_report.pdf (Manufacturing, P1)",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vani Raj",
            "user_id": "U117",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 2 - Karthik (User, Maintenance)
        {
            "timestamp": (base_date + timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Karthik S",
            "user_id": "U055",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.106",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=2, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Karthik S",
            "user_id": "U055",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: preventive_maintenance_log.pdf (Maintenance, P2)",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Karthik S",
            "user_id": "U055",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: equipment_breakdown_analysis.xlsx (Maintenance, P2)",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Karthik S",
            "user_id": "U055",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 2 - Priya (Approver, Procurement)
        {
            "timestamp": (base_date + timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Priya Nair",
            "user_id": "U072",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.105",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=3, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Priya Nair",
            "user_id": "U072",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: vendor_contracts_q2.pdf (Procurement, P4)",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=4, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Priya Nair",
            "user_id": "U072",
            "action": "DOCUMENT_APPROVED",
            "details": "Approved: vendor_contracts_q2.pdf",
        },
        {
            "timestamp": (base_date + timedelta(days=1, hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Priya Nair",
            "user_id": "U072",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 3 - Vikram (User, R&D)
        {
            "timestamp": (base_date + timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vikram Sharma",
            "user_id": "U102",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.107",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=1, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vikram Sharma",
            "user_id": "U102",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: prototype_testing_results.pdf (R&D, P1)",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=2, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vikram Sharma",
            "user_id": "U102",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: material_substitution_analysis.pdf (R&D, P1)",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Vikram Sharma",
            "user_id": "U102",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 3 - Meera (Manager, Operations)
        {
            "timestamp": (base_date + timedelta(days=2, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Meera Desai",
            "user_id": "U045",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.108",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=2, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Meera Desai",
            "user_id": "U045",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: ops_dashboard_extract.pdf (Operations, P3)",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Meera Desai",
            "user_id": "U045",
            "action": "DOCUMENT_APPROVED",
            "details": "Approved: ops_dashboard_extract.pdf",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Meera Desai",
            "user_id": "U045",
            "action": "LOGOUT",
            "details": "User logged out",
        },
        # Day 3 - Rajesh (User, Stores)
        {
            "timestamp": (base_date + timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rajesh Singh",
            "user_id": "U091",
            "action": "LOGIN",
            "details": "User logged in from 192.168.1.109",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=3, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rajesh Singh",
            "user_id": "U091",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: inventory_stock_report.xlsx (Stores, P2)",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=4, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rajesh Singh",
            "user_id": "U091",
            "action": "DOCUMENT_UPLOAD",
            "details": "Uploaded: material_inward_receipt.pdf (Stores, P2)",
        },
        {
            "timestamp": (base_date + timedelta(days=2, hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": "Rajesh Singh",
            "user_id": "U091",
            "action": "LOGOUT",
            "details": "User logged out",
        },
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if logs exist
    cursor.execute('SELECT COUNT(*) as count FROM system_logs')
    if cursor.fetchone()['count'] == 0:
        for log in system_logs:
            cursor.execute('''
                INSERT INTO system_logs (timestamp, user_name, user_id, action, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (log['timestamp'], log['user_name'], log['user_id'], log['action'], log['details']))
            print(f"[+] Created log: {log['action']} by {log['user_name']}")
        conn.commit()
    
    conn.close()


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Smart DMS - Database Seeding")
    print("=" * 60)
    print()
    
    print("📝 Seeding users...")
    seed_users()
    print()
    
    print("📄 Seeding documents...")
    seed_documents()
    print()
    
    print("📦 Seeding archive...")
    seed_archive()
    print()
    
    print("📋 Seeding system logs...")
    seed_system_logs()
    print()
    
    print("=" * 60)
    print("✅ Database seeding completed successfully!")
    print("=" * 60)
    print()
    print("Demo Users:")
    print("-" * 60)
    demo_users = [
        ("diva@example.com", "Pass@12345", "Admin"),
        ("arun@example.com", "Prod@12345", "Manager"),
        ("sneha@example.com", "Eng@12345", "Approver"),
        ("rahul@example.com", "Safe@12345", "User"),
    ]
    for email, password, role in demo_users:
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Role: {role}")
        print()


if __name__ == "__main__":
    main()
