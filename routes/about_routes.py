from flask import Blueprint, render_template, redirect, url_for
from services.document_library_service import DocumentLibraryService
from services.auth_service import AuthService

about_bp = Blueprint('about', __name__)

COMPANY = {
    "name": "ZF Rane Automotive India Private Limited",
    "formerly": "Formerly Rane TRW Steering Systems Private Limited",
    "overview": (
        "ZF Rane Automotive India Private Limited is a joint venture between "
        "Rane Group and ZF Group, Germany. The company designs, develops, and "
        "manufactures advanced steering gear systems for passenger and "
        "commercial vehicles, serving leading automotive manufacturers in "
        "India and global markets."
    ),
    "profile": [
        {"label": "Founded", "value": "1987"},
        {"label": "Headquarters", "value": "Chennai, India"},
        {"label": "Industry", "value": "Motor Vehicle Manufacturing"},
        {"label": "Company size", "value": "1,001-5,000 employees"},
    ],
    "highlights": [
        {
            "label": "Vision",
            "title": "Technology leadership",
            "description": (
                "To be a preferred provider of advanced steering system "
                "solutions through technology leadership and operational "
                "excellence."
            ),
        },
        {
            "label": "Products",
            "title": "Advanced steering systems",
            "description": (
                "Hydraulic and electric power steering systems engineered for "
                "evolving safety, performance, efficiency, and regulatory "
                "requirements."
            ),
        },
        {
            "label": "Engineering",
            "title": "In-house development and validation",
            "description": (
                "Complete-system design, application engineering, 3D "
                "modelling, simulation, FE analysis, CFD, and comprehensive "
                "strength, environmental, noise, fatigue, and durability testing."
            ),
        },
        {
            "label": "Manufacturing",
            "title": "Four facilities",
            "description": (
                "A manufacturing footprint spanning four facilities across "
                "Trichy, Chennai, and Pantnagar supports production capacity "
                "and supply reliability."
            ),
        },
    ],
    "sources": [
        {
            "label": "Rane Group company profile",
            "url": "https://ranegroup.com/group-companies/zf-rane-automotive-india-private-limited/",
        },
        {
            "label": "ZF Rane on LinkedIn",
            "url": "https://www.linkedin.com/company/zrai/about/",
        },
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
        "P2 - Guduvanchery Plant",
        "P3 - Guduvanchery Plant",
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
            "description": "Browse QMS, CSR, Core Tools Manuals, Customer Score Cards, EOHMS, and Awards and Certifications.",
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
            "description": "Use your GEN ID or email credentials. New users register with plant and department details before access is assigned.",
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
        company=COMPANY,
        system=TRACK_MY_DOCS,
        library_categories=DocumentLibraryService.get_categories(),
    )


@about_bp.route('/about/track-docs', endpoint='about_track_docs')
def about_track_docs():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return render_template('about_track_docs.html', system=TRACK_MY_DOCS)
