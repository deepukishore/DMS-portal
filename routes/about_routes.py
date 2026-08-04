from flask import Blueprint, render_template, redirect, url_for
from data.customers import OFFICIAL_CUSTOMERS
from services.document_library_service import DocumentLibraryService
from services.auth_service import AuthService

about_bp = Blueprint('about', __name__)

COMPANY = {
    "name": "ZF Rane Automotive India Private Limited",
    "formerly": "Formerly: Rane TRW Steering Systems Private Limited",
    "cin": "U35999TN1987PTC014600",
    "employees": "~2,600+",
    "registered_office": "Maithri, 132, Cathedral Road, Chennai, Tamil Nadu – 600086",
    "incorporated": "1987",
    "divisions": [
        {
            "id": "SGD",
            "name": "Steering Gear Division",
            "vision": "To be a Leader in Domestic Hydraulic Power Steering Business, Launch CV Electric Steering and Enhance Global Presence",
            "products": [
                "Rack & Pinion Steering Gears (Passenger Cars & Utility Vehicles)",
                "Re-circulating Ball Type Steering Gears (Commercial Vehicles)",
                "Hydraulic Power Steering Pumps — Vane, Variable Displacement, Dual Displacement",
                "Steering Reservoirs and complete assemblies",
            ],
            "plants": "P1 (Trichy), P2 & P3 (Guduvachery), P4 (Rudrapur)",
        },
        {
            "id": "OSD",
            "name": "Occupant Safety Division",
            "vision": "To be a preferred supplier of Occupant Restraint Systems, with a commitment to Safety",
            "products": [
                "Seat Belt Systems",
                "Airbag Components",
                "Occupant Restraint Systems for PC, UV & CV",
            ],
            "plants": "P1 (Trichy), P2 & P3 (Guduvachery)",
        },
    ],
    "plants": [
        {"id": "P1", "name": "Trichy Plant",       "location": "Tiruchirappalli, Tamil Nadu", "division": "SGD + OSD", "products": "Steering gears, Seat belts, Airbag systems"},
        {"id": "P2", "name": "Guduvachery Plant",  "location": "Guduvachery, Tamil Nadu",    "division": "SGD + OSD", "products": "Power steering pumps, Occupant safety"},
        {"id": "P3", "name": "Guduvachery Plant",  "location": "Guduvachery, Tamil Nadu",    "division": "SGD + OSD", "products": "Steering assemblies, Safety systems"},
        {"id": "P4", "name": "Uttarakhand Plant",  "location": "Rudrapur, Uttarakhand",      "division": "SGD",       "products": "Hydraulic power steering systems"},
    ],
    "customers": list(OFFICIAL_CUSTOMERS),
    "certifications": [
        {"icon": "✅", "text": "IATF 16949 : 2016 — Automotive Quality Management System"},
        {"icon": "✅", "text": "ISO 14001 : 2015 — Environmental Management System"},
        {"icon": "✅", "text": "OHSAS 18001 — Occupational Health & Safety"},
        {"icon": "✅", "text": "ASES Certified Plants"},
        {"icon": "✅", "text": "MSES Certified Plants"},
        {"icon": "✅", "text": "FORD Q1 Award"},
    ],
    "awards": [
        {"icon": "🏆", "text": "Winner of the Deming Prize"},
        {"icon": "🏆", "text": "Winner of the Japan Quality Medal (JQM) — highest quality honour in manufacturing"},
        {"icon": "🏆", "text": "Kia India — Excellence in Cooperation and Support Award (OSD)"},
        {"icon": "🏆", "text": "Ashok Leyland — Impactful Innovation in Defence Category (SGD)"},
        {"icon": "🏆", "text": "Escorts Kubota — Best Technology and Innovation Supplier Award (SGD)"},
        {"icon": "🏆", "text": "Multiple CII National Kaizen Competition Gold Awards (2026)"},
    ],
    "tools": [
        {"cat": "CAD/CAM",  "items": "CATIA V4/V5, SolidWorks, Pro-E Wildfire, AutoCAD"},
        {"cat": "Analysis", "items": "COSMOS/FE Analysis, CFD (Computational Fluid Dynamics), AMESim"},
        {"cat": "Process",  "items": "Advanced PPAP, APQP, MSA, SPC methodologies"},
        {"cat": "Quality",  "items": "TQM practices across all plants"},
    ],
}

TRACK_MY_DOCS = {
    "name": "Smart DMS",
    "tagline": "Current document management and approval tracking portal for ZF Rane Automotive India PVT LTD, SGD.",
    "description": (
        "Smart DMS helps teams upload, review, approve, publish, track, "
        "archive, and audit controlled documents across plants, departments, "
        "customers, QMS levels, and document-library categories."
    ),
    "version": "2.0.0",
    "release": "Current portal build",
    "supported_plants": [
        "P1 - Trichy Plant",
        "P2 - Guduvachery Plant",
        "P3 - Guduvachery Plant",
        "P4 - Uttarakhand Plant",
    ],
    "features": [
        {
            "icon": "Upload",
            "title": "QMS-aware uploads",
            "description": "Submit PDF, Word, Excel, and PowerPoint files with plant, department, customer, document number, revision, and exact library folder path.",
        },
        {
            "icon": "Flow",
            "title": "Two-stage approvals",
            "description": "Route submissions to first approvers, then final approvers, with rejection comments, timestamps, email alerts, and in-app notifications.",
        },
        {
            "icon": "Library",
            "title": "Current document library",
            "description": "Browse QMS, CSR, Core Tools Manuals, Customer Score Cards, EOHMS, Awards and Certifications, and Plant Wise Documents.",
        },
        {
            "icon": "Track",
            "title": "Track approvals",
            "description": "Follow each upload from submission through first review, final approval, published, or rejected status.",
        },
        {
            "icon": "Search",
            "title": "Search and dashboards",
            "description": "Filter documents by file, uploader, document number, revision, category, customer, plant, department, date, and approval status.",
        },
        {
            "icon": "Audit",
            "title": "Audit and recovery",
            "description": "Keep revision history, system log entries, soft-deleted archive records, PDF viewing copies, and admin restore actions traceable.",
        },
    ],
    "key_benefits": [
        "One controlled place for current approved documents.",
        "Clear ownership, approval status, and revision context.",
        "Less manual follow-up through notifications and Track Approvals.",
        "Audit-ready activity logs, archive recovery, and version history.",
    ],
    "workflow": [
        {
            "title": "Sign in or register",
            "description": "Use your GENID or email credentials. New users register with plant and department details before access is assigned.",
        },
        {
            "title": "Upload to the right library path",
            "description": "Choose internal or customer-linked documents, select the controlled category and subfolder, add document and revision details, then submit.",
        },
        {
            "title": "Review through approvals",
            "description": "The first approver reviews the file and forwards approved items to final approval. Rejected items include comments for correction.",
        },
        {
            "title": "Track every request",
            "description": "Use Track Approvals to see progress for your uploads. Higher-level users can switch between their uploads and all documents.",
        },
        {
            "title": "Browse the approved library",
            "description": "Approved files appear in the Document Library and can be opened as in-browser PDF viewing copies.",
        },
        {
            "title": "Maintain versions and audit trail",
            "description": "Admins can upload new versions, review archive records, restore soft-deleted files, and inspect the System Log.",
        },
    ],
    "roles": [
        {
            "name": "Admin",
            "description": "Full access, final approval, document updates, archive, system log, and People management.",
        },
        {
            "name": "Manager / Supervisor / Approver",
            "description": "Higher-level access to review pending items, view admin sections, and track documents.",
        },
        {
            "name": "User",
            "description": "Upload, browse approved documents, track own approvals, and manage profile details.",
        },
    ],
    "qms_levels": [
        "L1 - HOD / Final Approver: all QMS files, final approval, edit and delete rights.",
        "L2 - Assistant Manager / Manager: all QMS files and first approval responsibility.",
        "L3 - Procedure Viewer: SOPs, IATF audit plans, records, and other reports.",
        "L4 - Checksheet Viewer: records-only access.",
    ],
    "system_info": [
        "Framework: Flask and Jinja templates",
        "Database: SQLite by default with MySQL migration support",
        "Supported files: PDF, Word, Excel, PowerPoint",
        "Viewing: browser PDF viewing copies where possible",
        "Access model: roles plus QMS levels L1-L4",
        "Theme: dark/light toggle in the top bar",
    ],
}


@about_bp.route('/about')
def index():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return render_template(
        'about.html',
        system=TRACK_MY_DOCS,
        library_categories=DocumentLibraryService.get_categories(),
    )


@about_bp.route('/about/company')
def company():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return render_template('about_company.html', company=COMPANY)


@about_bp.route('/about/company-info', endpoint='about_company')
def about_company():
    return company()


@about_bp.route('/about/track-docs', endpoint='about_track_docs')
def about_track_docs():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return render_template('about_track_docs.html', system=TRACK_MY_DOCS)
