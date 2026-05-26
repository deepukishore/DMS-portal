from data.customers import OFFICIAL_CUSTOMERS


LIBRARY_CATEGORIES = [
    {"key": "procedures", "label": "Procedures", "icon": "📋"},
    {"key": "standard_manuals", "label": "Standard Manuals", "icon": "📖"},
    {"key": "core_tools_manuals", "label": "Core Tools Manuals", "icon": "🔧"},
    {"key": "awards", "label": "Awards", "icon": "🏆"},
    {"key": "certifications", "label": "Certifications", "icon": "📜"},
]


CATEGORY_ALIASES = {
    "std_manual": {"key": "standard_manuals"},
    "core_tool_manuals": {"key": "core_tools_manuals"},
    "certification": {"key": "certifications"},
    "cq_manuals": {"key": "procedures", "primary": "cq_manuals"},
    "business_procedures": {"key": "procedures", "primary": "business_procedures"},
}


STANDARD_MANUAL_CUSTOMER_DOCS = {
    "AL - Ashok Leyland": [
        "al_standard_manual_rev04.pdf",
        "al_supplier_quality_manual.pdf",
    ],
    "TML - Tata Motors Limited": [
        "tml_standard_manual_issue07.pdf",
        "tml_document_retention_guideline.pdf",
    ],
    "M&M - Mahindra and Mahindra": [
        "mm_standard_manual_rev03.pdf",
        "mm_traceability_manual.pdf",
    ],
    "FML - Force Motors Limited": [
        "fml_standard_manual_rev02.pdf",
        "fml_special_characteristics_guide.pdf",
    ],
    "SML ISUZU": [
        "sml_standard_manual_rev05.pdf",
        "sml_control_plan_requirements.pdf",
    ],
    "Switch Mobility": [
        "switch_standard_manual_rev01.pdf",
        "switch_supplier_document_matrix.pdf",
    ],
    "VECV - Volvo Eicher Commercial Vehicles": [
        "vecv_standard_manual_rev06.pdf",
        "vecv_packaging_document_standard.pdf",
    ],
    "DICV - Daimler India Commercial Vehicles": [
        "dicv_standard_manual_rev08.pdf",
        "dicv_drawing_change_control_manual.pdf",
    ],
    "Renault Nissan": [
        "renault_nissan_standard_manual_rev03.pdf",
        "renault_nissan_supplier_spec_manual.pdf",
    ],
}


CORE_TOOLS_CUSTOMER_DOCS = {
    "AL - Ashok Leyland": [
        "al_apqp_customer_requirements.pdf",
        "al_ppap_submission_manual.pdf",
    ],
    "TML - Tata Motors Limited": [
        "tml_apqp_customer_requirements.pdf",
        "tml_msa_spc_expectations.pdf",
    ],
    "M&M - Mahindra and Mahindra": [
        "mm_ppap_customer_requirements.pdf",
        "mm_fmea_submission_format.pdf",
    ],
    "FML - Force Motors Limited": [
        "fml_ppap_submission_matrix.pdf",
        "fml_spc_control_guideline.pdf",
    ],
    "SML ISUZU": [
        "sml_ppap_customer_requirements.pdf",
        "sml_gauge_rr_submission_guide.pdf",
    ],
    "Switch Mobility": [
        "switch_apqp_customer_requirements.pdf",
        "switch_process_capability_manual.pdf",
    ],
    "VECV - Volvo Eicher Commercial Vehicles": [
        "vecv_ppap_submission_manual.pdf",
        "vecv_control_plan_customer_format.pdf",
    ],
    "DICV - Daimler India Commercial Vehicles": [
        "dicv_apqp_customer_requirements.pdf",
        "dicv_process_audit_core_tools_guide.pdf",
    ],
    "Renault Nissan": [
        "renault_nissan_ppap_requirements.pdf",
        "renault_nissan_core_tools_reference.pdf",
    ],
}


LIBRARY_DATA = {
    "procedures": {
        "description": "Browse procedures by manual type or business orientation.",
        "primary_options": {
            "cq_manuals": {
                "label": "CQ Manuals",
                "full_label": "CQ Manuals - Customer Quality Manuals",
                "description": "Customer quality manuals and controlled reference documents.",
                "files": [
                    "customer_quality_manual_master_index.pdf",
                    "supplier_quality_manual_compendium.pdf",
                    "customer_specific_quality_requirements_matrix.xlsx",
                    "quality_manual_revision_register.pdf",
                ],
            },
            "business_procedures": {
                "label": "Business Procedures",
                "description": "Business procedures organized by orientation.",
                "secondary_options": {
                    "management_oriented": {
                        "label": "Management Oriented",
                        "description": "Leadership, review, and policy-driven procedures.",
                        "files": [
                            "management_review_procedure.pdf",
                            "business_planning_procedure.pdf",
                            "risk_management_procedure.docx",
                            "document_control_master_procedure.pdf",
                        ],
                    },
                    "customer_oriented": {
                        "label": "Customer Oriented",
                        "description": "Procedures tied to customer communication and delivery.",
                        "files": [
                            "customer_complaint_handling_procedure.pdf",
                            "customer_change_request_procedure.docx",
                            "order_fulfillment_business_procedure.pdf",
                            "customer_scorecard_response_matrix.xlsx",
                        ],
                    },
                    "support_oriented": {
                        "label": "Support Oriented",
                        "description": "Support-function procedures for enabling teams.",
                        "files": [
                            "training_and_competency_procedure.pdf",
                            "maintenance_support_procedure.docx",
                            "procurement_support_workflow.pdf",
                            "it_backup_and_restore_procedure.pdf",
                        ],
                    },
                    "plant_procedures": {
                        "label": "Plant Procedures",
                        "description": "Procedures covering all four plants with consolidated plant-level workflows.",
                        "files": [
                            "plant_procedures_overview.pdf",
                            "plant_health_safety_guidelines.pdf",
                            "equipment_maintenance_for_all_plants.docx",
                            "plant_operational_coordinations.xlsx",
                        ],
                    },
                },
            },
        },
    },
    "standard_manuals": {
        "description": "Browse standard manuals by source.",
        "primary_options": {
            "rane_docs": {
                "label": "Rane Docs",
                "description": "Internal standard manuals maintained by Rane.",
                "files": [
                    "rane_standard_manual_issue_12.pdf",
                    "process_standardization_manual.docx",
                    "internal_document_control_standard.pdf",
                    "master_work_instruction_format.xlsx",
                ],
            },
            "customer_docs": {
                "label": "Customer Docs",
                "description": "Customer-specific standard manuals.",
                "customers": STANDARD_MANUAL_CUSTOMER_DOCS,
            },
        },
    },
    "core_tools_manuals": {
        "description": "Browse core tools manuals by source.",
        "primary_options": {
            "rane_docs": {
                "label": "Rane Docs",
                "description": "Internal APQP, PPAP, FMEA, MSA, and SPC references.",
                "files": [
                    "rane_apqp_manual_rev09.pdf",
                    "rane_ppap_submission_manual.pdf",
                    "rane_process_fmea_handbook.docx",
                    "rane_spc_msa_reference_guide.pdf",
                ],
            },
            "customer_docs": {
                "label": "Customer Docs",
                "description": "Customer-specific core tools references.",
                "customers": CORE_TOOLS_CUSTOMER_DOCS,
            },
        },
    },
    "awards": {
        "description": "Company awards and recognition documents.",
        "files": [
            "best_supplier_award_2024.pdf",
            "quality_excellence_award_2025.pdf",
            "operational_excellence_recognition.pdf",
            "customer_appreciation_award_switch_mobility.pdf",
        ],
    },
    "certifications": {
        "description": "Certifications and compliance documents.",
        "files": [
            "iatf_16949_certificate.pdf",
            "iso_14001_certificate.pdf",
            "iso_45001_certificate.pdf",
            "customer_specific_certification_register.xlsx",
        ],
    },
}


for customer in OFFICIAL_CUSTOMERS:
    LIBRARY_DATA["standard_manuals"]["primary_options"]["customer_docs"]["customers"].setdefault(
        customer, []
    )
    LIBRARY_DATA["core_tools_manuals"]["primary_options"]["customer_docs"]["customers"].setdefault(
        customer, []
    )
