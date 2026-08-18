VALID_DOCUMENT_CATEGORIES = {
    "qms",
    "csr",
    "core_tools_manuals",
    "customer_score_card",
    "eohms",
    "awards_certifications",
}

CATEGORY_ALIASES = {
    "master_records": "qms",
    "procedures": "qms",
    "cq_manuals": "qms",
    "business_procedures": "qms",
    "standard_manuals": "csr",
    "std_manual": "csr",
    "core_tool_manuals": "core_tools_manuals",
    "awards": "awards_certifications",
    "certifications": "awards_certifications",
    "certification": "awards_certifications",
    "audit_nc": "qms",
}


def infer_document_category(record):
    """Return a valid library category for legacy or mock document records."""
    existing = str(record.get("category") or "").strip().lower()
    existing = CATEGORY_ALIASES.get(existing, existing)
    if existing in VALID_DOCUMENT_CATEGORIES:
        return existing

    file_name = " ".join(
        str(record.get(field) or "").lower()
        for field in ("file_name", "original_file_name", "document_number")
    )
    department = str(record.get("department") or "").lower()
    customer = str(record.get("customer") or "").strip().lower()

    if any(term in file_name for term in ("fmea", "ppap", "apqp", "control_plan", "control plan", "msa", "spc")):
        return "core_tools_manuals"
    if any(term in file_name for term in ("scorecard", "score_card", "score card", "kpi", "performance")):
        return "customer_score_card"
    if any(term in file_name for term in ("certificate", "certification", "award", "recognition")):
        return "awards_certifications"
    if any(term in file_name for term in ("safety", "incident", "ppe", "near_miss", "near miss", "environment", "eohs")):
        return "eohms"
    if "human resources" in department or department.startswith("hrd"):
        return "eohms"
    if customer:
        return "csr"
    return "qms"


def categorize_document_records(records):
    for record in records:
        record["category"] = infer_document_category(record)
    return records
