from flask import Blueprint, render_template, redirect, url_for
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
    "customers": [
        "Hyundai Motor India", "Tata Motors", "Ashok Leyland", "TVS Motor Company",
        "Maruti Suzuki", "Kia India", "Mahindra & Mahindra", "Volvo",
        "Renault-Nissan", "SML Isuzu", "Escorts Kubota",
    ],
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


@about_bp.route('/about')
def index():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return render_template('about.html')


@about_bp.route('/about/company')
def company():
    if not AuthService.is_logged_in():
        return redirect(url_for('auth.login'))
    return render_template('about_company.html', company=COMPANY)
