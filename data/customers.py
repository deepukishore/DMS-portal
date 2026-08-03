OFFICIAL_CUSTOMERS = [
    "TML - Tata Motors Limited",
    "AL - Ashok Leyland",
    "M&M - Mahindra and Mahindra",
    "VECV - Volvo Eicher Commercial Vehicles",
    "DICV - Daimler India Commercial Vehicles",
    "FML - Force Motors Limited",
    "Renault Nissan",
    "SML ISUZU",
    "Switch Mobility",
]


CUSTOMER_BRANDS = {
    "TML - Tata Motors Limited": {
        "display_name": "Tata Motors",
        "logo": "images/customers/tata-motors.svg",
    },
    "AL - Ashok Leyland": {
        "display_name": "Ashok Leyland",
        "logo": "images/customers/ashok-leyland.svg",
    },
    "M&M - Mahindra and Mahindra": {
        "display_name": "Mahindra and Mahindra",
        "logo": "images/customers/mahindra.webp",
    },
    "VECV - Volvo Eicher Commercial Vehicles": {
        "display_name": "VE Commercial Vehicles",
        "logo": "images/customers/vecv.png",
    },
    "DICV - Daimler India Commercial Vehicles": {
        "display_name": "Daimler India Commercial Vehicles",
        "logo": "images/customers/daimler-truck.svg",
    },
    "FML - Force Motors Limited": {
        "display_name": "Force Motors",
        "logo": "images/customers/force-motors.svg",
    },
    "Renault Nissan": {
        "display_name": "Renault Nissan",
        "logo": "images/customers/renault-nissan.svg",
    },
    "SML ISUZU": {
        "display_name": "SML ISUZU",
        "logo": "images/customers/sml-isuzu.svg",
        "banner_tone": "red",
    },
    "Switch Mobility": {
        "display_name": "Switch Mobility",
        "logo": "images/customers/switch-mobility.svg",
    },
}


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
    "Renault-Nissan": "Renault Nissan",
    "AL - Ashok Leyland": "AL - Ashok Leyland",
    "TML - Tata Motors Limited": "TML - Tata Motors Limited",
    "M&M - Mahindra and Mahindra": "M&M - Mahindra and Mahindra",
    "FML - Force Motors Limited": "FML - Force Motors Limited",
    "SML ISUZU": "SML ISUZU",
    "SML Mahindra": "SML ISUZU",
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


def customer_query_values(customer):
    """Return the canonical customer plus legacy values still stored in older rows."""
    canonical = normalize_customer(customer)
    values = [canonical]
    values.extend(
        legacy
        for legacy, normalized in LEGACY_CUSTOMER_MAP.items()
        if normalized == canonical and legacy != canonical
    )
    return values


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


def sort_customers(customers):
    """Return unique customer names in the official business order."""
    order = {customer: index for index, customer in enumerate(OFFICIAL_CUSTOMERS)}
    normalized = []
    seen = set()
    for customer in customers:
        customer_name = normalize_customer(customer)
        if not customer_name or customer_name in seen:
            continue
        normalized.append(customer_name)
        seen.add(customer_name)
    return sorted(
        normalized,
        key=lambda customer: (
            order.get(customer, len(order)),
            customer.casefold(),
        ),
    )
