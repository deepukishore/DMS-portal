OFFICIAL_CUSTOMERS = [
    "AL - Ashok Leyland",
    "TML - Tata Motors Limited",
    "M&M - Mahindra and Mahindra",
    "FML - Force Motors Limited",
    "SML ISUZU",
    "Switch Mobility",
    "VECV - Volvo Eicher Commercial Vehicles",
    "DICV - Daimler India Commercial Vehicles",
    "Renault Nissan",
]


CUSTOMER_FILTERS = ["Internal", *OFFICIAL_CUSTOMERS]


LEGACY_CUSTOMER_MAP = {
    "Ashok Leyland": "AL - Ashok Leyland",
    "Tata Motors": "TML - Tata Motors Limited",
    "Tata Motors Limited": "TML - Tata Motors Limited",
    "Hyundai Motors": "M&M - Mahindra and Mahindra",
    "Mahindra and Mahindra": "M&M - Mahindra and Mahindra",
    "TVS Motors": "Switch Mobility",
    "Force Motors": "FML - Force Motors Limited",
    "Volvo Eicher Commercial Vehicles": "VECV - Volvo Eicher Commercial Vehicles",
    "Daimler India Commercial Vehicles": "DICV - Daimler India Commercial Vehicles",
    "AL - Ashok Leyland": "AL - Ashok Leyland",
    "TML - Tata Motors Limited": "TML - Tata Motors Limited",
    "M&M - Mahindra and Mahindra": "M&M - Mahindra and Mahindra",
    "FML - Force Motors Limited": "FML - Force Motors Limited",
    "SML ISUZU": "SML ISUZU",
    "Switch Mobility": "Switch Mobility",
    "VECV - Volvo Eicher Commercial Vehicles": "VECV - Volvo Eicher Commercial Vehicles",
    "DICV - Daimler India Commercial Vehicles": "DICV - Daimler India Commercial Vehicles",
    "Renault Nissan": "Renault Nissan",
}


def normalize_customer(customer):
    if customer is None:
        return customer
    cleaned = " ".join(str(customer).split())
    if not cleaned:
        return "Internal"
    if cleaned == "Internal":
        return cleaned
    return LEGACY_CUSTOMER_MAP.get(cleaned, cleaned)


def normalize_customer_records(records):
    normalized = []
    for record in records:
        item = dict(record)
        if "customer" in item:
            item["customer"] = normalize_customer(item["customer"])
        normalized.append(item)
    return normalized


def normalize_customer_keys(mapping):
    return {
        normalize_customer(customer): value
        for customer, value in mapping.items()
    }
