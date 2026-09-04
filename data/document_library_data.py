from data.customers import OFFICIAL_CUSTOMERS
from data.mock_data import MASTER_RECORD_PLANTS, PLANTS


LIBRARY_CATEGORIES = [
    {
        "key": "qms",
        "label": "Quality Management System",
        "dashboard_label": "Quality Management System",
        "icon": "Q",
        "icon_image": "images/library-icons/qms.svg",
        "folder_image": "images/library-folders/qms.jpg",
    },
    {
        "key": "csr",
        "label": "Customer Specific Requirements",
        "dashboard_label": "Customer Specific Requirements",
        "icon": "C",
        "icon_image": "images/library-icons/csr.svg",
        "folder_image": "images/library-folders/csr.png",
    },
    {
        "key": "core_tools_manuals",
        "label": "Core Tools Manuals",
        "dashboard_label": "Core Tools Manuals",
        "icon": "T",
        "icon_image": "images/library-icons/core-tools-manuals.svg",
        "folder_image": "images/library-folders/core-tools-manuals.jpeg",
    },
    {
        "key": "customer_score_card",
        "label": "Customer Score Card",
        "dashboard_label": "Customer Score Card",
        "icon": "S",
        "icon_image": "images/library-icons/customer-score-card.svg",
        "folder_image": "images/library-folders/customer-score-card.jpg",
    },
    {
        "key": "eohms",
        "label": "Environment, Occupational Health and Safety Management System",
        "dashboard_label": "Environment, Occupational Health and Safety Management System",
        "icon": "E",
        "icon_image": "images/library-icons/eohms.svg",
        "folder_image": "images/library-folders/eohms.jpg",
    },
    {
        "key": "awards_certifications",
        "label": "Awards and Certifications",
        "dashboard_label": "Awards and Certifications",
        "icon": "A",
        "icon_image": "images/library-icons/awards-certifications.svg",
        "folder_image": "images/library-folders/awards-certifications.png",
    },
]


CATEGORY_ALIASES = {
    "procedures": {"key": "qms"},
    "cq_manuals": {"key": "qms", "primary": "L1"},
    "business_procedures": {"key": "qms", "secondary": "business_procedures"},
    "standard_manuals": {"key": "csr"},
    "std_manual": {"key": "csr"},
    "core_tool_manuals": {"key": "core_tools_manuals"},
    "awards": {"key": "awards_certifications", "primary": "awards"},
    "certifications": {"key": "awards_certifications", "primary": "certifications"},
    "certification": {"key": "awards_certifications", "primary": "certifications"},
    # Keep old bookmarks working while presenting IATF Audit inside QMS.
    "audit_nc": {"key": "qms", "secondary": "iatf_audit"},
    # Keep older bookmarks routed to the main QMS library when the standalone plant-wise view is removed.
    "master_records": {"key": "qms"},
}


def _audit_plant_file_map(audit_scope, document_type):
    return {
        plant["label"]: [
            f"{plant['id'].lower().replace('&', 'and')}_{audit_scope}_{document_type}.pdf",
            f"{plant['id'].lower().replace('&', 'and')}_{audit_scope}_{document_type}_register.xlsx",
        ]
        for plant in PLANTS
    }


def _auditor_plant_pdf_map(auditor_type):
    return {
        plant["label"]: [
            f"{plant['id'].lower().replace('&', 'and')}_{auditor_type}_list.pdf",
        ]
        for plant in PLANTS
    }


QMS_DOCUMENT_GROUPS = {
    "quality_manuals": {
        "label": "Quality Manuals",
        "files": [
            "quality_manual_master_index.pdf",
            "qms_quality_policy_manual.pdf",
            "quality_manual_revision_register.xlsx",
        ],
    },
    "business_procedures": {
        "label": "Business Procedures",
        "secondary_options": {
            "bp_cp": {
                "label": "BP - CP",
                "description": "Business procedure CP documents.",
                "files": [
                    "bp_cp_business_planning_procedure.pdf",
                    "bp_cp_document_control_procedure.docx",
                ],
            },
            "bp_mp": {
                "label": "BP - MP",
                "description": "Business procedure MP documents.",
                "files": [
                    "bp_mp_management_review_procedure.pdf",
                    "bp_mp_process_monitoring_procedure.xlsx",
                ],
            },
            "bp_sp": {
                "label": "BP - SP",
                "description": "Business procedure SP documents.",
                "files": [
                    "bp_sp_risk_and_opportunity_procedure.docx",
                    "bp_sp_support_process_procedure.pdf",
                ],
            },
        },
    },
    "sops": {
        "label": "SOPs",
        "plant_departments": {
            "P1 - Trichy Plant": {
                "label": "P1 - Trichy Plant",
                "departments": {
                    "QAD - Quality Assurance Department": {
                        "files": [
                            "p1_sop_quality_manual.pdf",
                            "p1_sop_control_sheet.xlsx",
                        ],
                    },
                    "PED - Product Engineering Department": {
                        "files": [
                            "p1_sop_process_engineering.pdf",
                            "p1_sop_change_management.docx",
                        ],
                    },
                },
            },
            "P2 - Guduvanchery Plant": {
                "label": "P2 - Guduvanchery Plant",
                "departments": {
                    "MFG - Manufacturing": {
                        "files": [
                            "p2_sop_line_startup.pdf",
                            "p2_sop_machine_changeover.docx",
                        ],
                    },
                    "PLE - Plant Engineering": {
                        "files": [
                            "p2_sop_maintenance_plan.pdf",
                            "p2_sop_tooling_check.xlsx",
                        ],
                    },
                },
            },
            "P3 - Guduvanchery Plant": {
                "label": "P3 - Guduvanchery Plant",
                "departments": {
                    "MMD - Material Management Department": {
                        "files": [
                            "p3_sop_material_issue.pdf",
                            "p3_sop_store_dispatch.xlsx",
                        ],
                    },
                    "HRD - Human Resources Department": {
                        "files": [
                            "p3_sop_training_record.pdf",
                            "p3_sop_induction_checklist.docx",
                        ],
                    },
                },
            },
            "P4 - Uttarakhand Plant": {
                "label": "P4 - Uttarakhand Plant",
                "departments": {
                    "MED - Manufacturing Engineering Department": {
                        "files": [
                            "p4_sop_process_monitoring.pdf",
                            "p4_sop_quality_alert.xlsx",
                        ],
                    },
                    "PMD - Product Management Department": {
                        "files": [
                            "p4_sop_product_release.pdf",
                            "p4_sop_customer_response.docx",
                        ],
                    },
                },
            },
        },
    },
    "checklists": {
        "label": "Records",
        "plant_departments": {
            "P1 - Trichy Plant": {
                "label": "P1 - Trichy Plant",
                "departments": {
                    "QAD - Quality Assurance Department": {
                        "files": [
                            "p1_record_audit_checksheet.xlsx",
                            "p1_record_release_checksheet.pdf",
                        ],
                    },
                    "PED - Product Engineering Department": {
                        "files": [
                            "p1_record_engineering_change.xlsx",
                            "p1_record_validation_report.pdf",
                        ],
                    },
                },
            },
            "P2 - Guduvanchery Plant": {
                "label": "P2 - Guduvanchery Plant",
                "departments": {
                    "MFG - Manufacturing": {
                        "files": [
                            "p2_record_shift_report.xlsx",
                            "p2_record_closure_checksheet.pdf",
                        ],
                    },
                    "PLE - Plant Engineering": {
                        "files": [
                            "p2_record_maintenance_record.xlsx",
                            "p2_record_breakdown_report.pdf",
                        ],
                    },
                },
            },
            "P3 - Guduvanchery Plant": {
                "label": "P3 - Guduvanchery Plant",
                "departments": {
                    "MMD - Material Management Department": {
                        "files": [
                            "p3_record_store_receipt.xlsx",
                            "p3_record_material_inspection.pdf",
                        ],
                    },
                    "HRD - Human Resources Department": {
                        "files": [
                            "p3_record_training_attendance.xlsx",
                            "p3_record_induction_form.pdf",
                        ],
                    },
                },
            },
            "P4 - Uttarakhand Plant": {
                "label": "P4 - Uttarakhand Plant",
                "departments": {
                    "MED - Manufacturing Engineering Department": {
                        "files": [
                            "p4_record_process_monitor.xlsx",
                            "p4_record_nonconformance_report.pdf",
                        ],
                    },
                    "PMD - Product Management Department": {
                        "files": [
                            "p4_record_customer_feedback.xlsx",
                            "p4_record_release_summary.pdf",
                        ],
                    },
                },
            },
        },
    },
    "other_reports": {
        "label": "IATF Standards",
        "files": [
            "monthly_qms_performance_report.pdf",
            "customer_complaint_trend_report.xlsx",
            "corrective_action_status_report.pdf",
        ],
    },
    "sanction_interpretation": {
        "label": "IATF Sanction Interpretation",
        "files": [
            "sanction_interpretation_guideline.pdf",
            "sanction_interpretation_register.xlsx",
            "sanction_interpretation_review_form.docx",
        ],
    },
    "iatf_audit": {
        "label": "IATF Audit Reports",
        "description": "IATF audit reports and auditor lists organized by folder and plant.",
        "secondary_options": {
            "plans": {
                "label": "Plans",
                "description": "IATF audit plans and planning records.",
                "files": [
                    "quality_objective_plan.xlsx",
                    "internal_audit_plan.pdf",
                    "management_review_plan.docx",
                ],
            },
            "internal_audit_ncs": {
                "label": "Internal Audit - NCs",
                "description": "Internal audit non-conformance documents by plant.",
                "plants": _audit_plant_file_map("internal_audit", "ncs"),
            },
            "internal_audit_reports": {
                "label": "Internal Audit - Reports",
                "description": "Internal audit reports by plant.",
                "plants": _audit_plant_file_map("internal_audit", "reports"),
            },
            "external_audit_ncs": {
                "label": "External Audit - NCs",
                "description": "External audit non-conformance documents by plant.",
                "plants": _audit_plant_file_map("external_audit", "ncs"),
            },
            "external_audit_reports": {
                "label": "External Audit - Reports",
                "description": "External audit reports by plant.",
                "plants": _audit_plant_file_map("external_audit", "reports"),
            },
            "auditors_list": {
                "label": "Auditors List",
                "description": "Select an auditor list, then select a plant to open its PDF.",
                "secondary_options": {
                    "supplier_auditor_list": {
                        "label": "Supplier Auditor List",
                        "description": "Supplier auditor list PDF organized by plant.",
                        "plants": _auditor_plant_pdf_map("supplier_auditor"),
                    },
                    "internal_auditor_list": {
                        "label": "Internal Auditor List",
                        "description": "Internal auditor list PDF organized by plant.",
                        "plants": _auditor_plant_pdf_map("internal_auditor"),
                    },
                },
            },
        },
    },
}


QMS_LEVELS = {
    "L1": {
        "label": "L1 - HOD / Final Approver",
        "description": "HOD level users with access to every QMS document and final approval responsibility.",
        "access": "All QMS files",
        "can_edit": True,
        "can_delete": True,
        "approver": True,
        "groups": list(QMS_DOCUMENT_GROUPS.keys()),
    },
    "L2": {
        "label": "L2 - Assistant Manager / Manager",
        "description": "First approvers who review uploaded documents, select sharing recipients, and send them to L1 for final approval.",
        "access": "All QMS files",
        "can_edit": False,
        "can_delete": False,
        "approver": True,
        "groups": list(QMS_DOCUMENT_GROUPS.keys()),
    },
    "L3": {
        "label": "L3 - Procedure Viewer",
        "description": "Can view SOPs, IATF audit plans, records, and IATF standards.",
        "access": "SOPs, IATF audit plans, records, and IATF standards",
        "can_edit": False,
        "can_delete": False,
        "approver": False,
        "groups": ["sops", "iatf_audit", "checklists", "other_reports"],
        "subgroups": {"iatf_audit": ["plans"]},
    },
    "L4": {
        "label": "L4 - Checksheet Viewer",
        "description": "Can only view records.",
        "access": "Records only",
        "can_edit": False,
        "can_delete": False,
        "approver": False,
        "groups": ["checklists"],
    },
}


def _customer_file_map(prefix, suffix):
    return {
        customer: [
            f"{prefix}_{customer.split(' - ')[0].lower().replace('&', 'and').replace(' ', '_')}_{suffix}.pdf",
            f"{prefix}_{customer.split(' - ')[0].lower().replace('&', 'and').replace(' ', '_')}_revision_register.xlsx",
        ]
        for customer in OFFICIAL_CUSTOMERS
    }


CSR_CUSTOMER_MANUALS = _customer_file_map("csr_manual", "requirements")
CSR_CUSTOMER_INITIATIVES = _customer_file_map("customer_initiative", "summary")
CUSTOMER_SCORE_CARDS = _customer_file_map("score_card", "monthly_summary")


LIBRARY_DATA = {
    "qms": {
        "description": "Quality Management System documents organized by L1 to L4 access hierarchy.",
        "levels": QMS_LEVELS,
        "document_groups": QMS_DOCUMENT_GROUPS,
        "plant_options": PLANTS,
    },
    "csr": {
        "description": "Customer Specific Requirement documents.",
        "primary_options": {
            "csr_matrix": {
                "label": "CSR Matrix",
                "description": "Customer specific requirement matrix and trackers.",
                "files": [
                    "csr_matrix_master.xlsx",
                    "csr_compliance_tracker.pdf",
                    "customer_requirement_cross_reference.xlsx",
                ],
            },
            "customer_manual": {
                "label": "Customer Manual",
                "description": "Select a customer to view related manuals.",
                "customers": CSR_CUSTOMER_MANUALS,
            },
            "customer_initiatives": {
                "label": "Customer Initiatives",
                "description": "Select a customer to view initiative documents and supporting records.",
                "customers": CSR_CUSTOMER_INITIATIVES,
            },
        },
    },
    "core_tools_manuals": {
        "description": "Core tools manuals and reference documents organized by tool.",
        "primary_options": {
            "ppap": {
                "label": "PPAP - Production Part Approval Process",
                "description": "Production Part Approval Process manuals and submission references.",
                "files": [
                    "ppap_production_part_approval_process_manual.pdf",
                    "ppap_submission_requirements.xlsx",
                ],
            },
            "msa": {
                "label": "MSA - Measurement Systems Analysis",
                "description": "Measurement Systems Analysis manuals and study templates.",
                "files": [
                    "msa_measurement_systems_analysis_manual.pdf",
                    "msa_gauge_rr_study_template.xlsx",
                ],
            },
            "fmea": {
                "label": "FMEA - Failure Mode and Effects Analysis",
                "description": "Failure Mode and Effects Analysis manuals and worksheets.",
                "files": [
                    "fmea_failure_mode_effects_analysis_manual.pdf",
                    "fmea_analysis_worksheet.xlsx",
                ],
            },
            "apqp": {
                "label": "APQP - Advanced Product Quality Planning",
                "description": "Advanced Product Quality Planning manuals and trackers.",
                "files": [
                    "apqp_advanced_product_quality_planning_manual.pdf",
                    "apqp_project_tracker.xlsx",
                ],
            },
            "spc": {
                "label": "SPC - Statistical Process Control",
                "description": "Statistical Process Control manuals and reference documents.",
                "files": [
                    "spc_statistical_process_control_manual.pdf",
                    "spc_control_chart_reference.xlsx",
                ],
            },
            "cp": {
                "label": "CP - Control Plan",
                "description": "Control Plan manuals, formats, and reference documents.",
                "files": [
                    "cp_control_plan_manual.pdf",
                    "cp_control_plan_template.xlsx",
                ],
            },
        },
    },
    "customer_score_card": {
        "description": "Customer score cards organized by customer.",
        "customers": CUSTOMER_SCORE_CARDS,
    },
    "eohms": {
        "description": "EOHMS manual and related documents.",
        "files": [
            "eohms_manual.pdf",
            "environmental_operational_control_procedure.pdf",
            "health_and_safety_risk_register.xlsx",
            "eohms_legal_compliance_register.pdf",
        ],
    },
    "awards_certifications": {
        "description": "Awards, certificates, and recognition documents.",
        "primary_options": {
            "awards": {
                "label": "Awards",
                "description": "Company awards and customer recognition.",
                "files": [
                    "best_supplier_award_2024.pdf",
                    "quality_excellence_award_2025.pdf",
                    "customer_appreciation_award.pdf",
                ],
            },
            "certifications": {
                "label": "Certifications",
                "description": "Compliance and management-system certificates.",
                "files": [
                    "iatf_16949_certificate.pdf",
                    "iso_14001_certificate.pdf",
                    "iso_45001_certificate.pdf",
                ],
            },
        },
    },
    "audit_nc": {
        "description": "IATF internal and external audit records organized by document type and plant.",
        "plant_options": PLANTS,
        "primary_options": {
            "internal_audit": {
                "label": "Internal Audit",
                "description": "Internal IATF audit non-conformances and reports.",
                "secondary_options": {
                    "ncs": {
                        "label": "NCs",
                        "description": "Select a plant to view internal audit non-conformance documents.",
                        "plants": _audit_plant_file_map("internal_audit", "ncs"),
                    },
                    "reports": {
                        "label": "Reports",
                        "description": "Select a plant to view internal audit reports.",
                        "plants": _audit_plant_file_map("internal_audit", "reports"),
                    },
                },
            },
            "external_audit": {
                "label": "External Audit",
                "description": "External IATF audit non-conformances and reports.",
                "secondary_options": {
                    "ncs": {
                        "label": "NCs",
                        "description": "Select a plant to view external audit non-conformance documents.",
                        "plants": _audit_plant_file_map("external_audit", "ncs"),
                    },
                    "reports": {
                        "label": "Reports",
                        "description": "Select a plant to view external audit reports.",
                        "plants": _audit_plant_file_map("external_audit", "reports"),
                    },
                },
            },
        },
    },
    "plant_wise_records": {
        "description": "Approved records organized by plant and department.",
        "plants": MASTER_RECORD_PLANTS,
    },
}
