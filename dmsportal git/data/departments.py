OFFICIAL_DEPARTMENT_MAP = {
    "MED": "Manufacturing Engineering Department",
    "MFG": "Manufacturing",
    "MFG HT": "Manufacturing Heat Treatment",
    "PED": "Product Engineering Department",
    "PLE": "Plant Engineering",
    "MMD": "Material Management Department",
    "QAD": "Quality Assurance Department",
    "HRD": "Human Resources Department",
}


OFFICIAL_DEPARTMENTS = [
    f"{code} - {label}" for code, label in OFFICIAL_DEPARTMENT_MAP.items()
]


LEGACY_DEPARTMENT_MAP = {
    "Quality": "QAD - Quality Assurance Department",
    "Production": "MFG - Manufacturing",
    "Manufacturing": "MFG - Manufacturing",
    "Operations": "MFG - Manufacturing",
    "Engineering": "PED - Product Engineering Department",
    "R&D": "PED - Product Engineering Department",
    "Maintenance": "PLE - Plant Engineering",
    "Procurement": "MMD - Material Management Department",
    "Stores": "MMD - Material Management Department",
    "Safety": "HRD - Human Resources Department",
    "Process Engineering Department": "PED - Product Engineering Department",
    "Plant Layout Engineering": "PLE - Plant Engineering",
    "Materials Management Department": "MMD - Material Management Department",
    "Manufacturing (Heat Treatment)": "MFG HT - Manufacturing Heat Treatment",
    "MFG-HT": "MFG HT - Manufacturing Heat Treatment",
}


DEPARTMENT_ALIASES = {
    **LEGACY_DEPARTMENT_MAP,
    **{code: f"{code} - {label}" for code, label in OFFICIAL_DEPARTMENT_MAP.items()},
    **{
        label: f"{code} - {label}"
        for code, label in OFFICIAL_DEPARTMENT_MAP.items()
    },
    **{
        f"{code} - {label}": f"{code} - {label}"
        for code, label in OFFICIAL_DEPARTMENT_MAP.items()
    },
}


def normalize_department(department):
    if not department:
        return department
    cleaned = " ".join(str(department).split())
    return DEPARTMENT_ALIASES.get(cleaned, cleaned)


def normalize_records(records):
    normalized = []
    for record in records:
        item = dict(record)
        if "department" in item:
            item["department"] = normalize_department(item["department"])
        normalized.append(item)
    return normalized


def normalize_user_map(users):
    return {
        email: {**user, "department": normalize_department(user.get("department", ""))}
        for email, user in users.items()
    }


def normalize_department_keys(mapping):
    return {
        normalize_department(department): value
        for department, value in mapping.items()
    }


def normalize_nested_department_keys(mapping):
    return {
        outer_key: normalize_department_keys(inner_mapping)
        for outer_key, inner_mapping in mapping.items()
    }
