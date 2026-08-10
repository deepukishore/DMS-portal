import re


_PLANT_CODE_PATTERN = re.compile(r"^\s*(P\d+(?:\s*&\s*\d+)?)\b", re.IGNORECASE)


def plant_code(value):
    """Return the compact plant identifier while preserving unknown values."""
    if value is None:
        return ""

    text = str(value).strip()
    match = _PLANT_CODE_PATTERN.match(text)
    if not match:
        return text

    return re.sub(r"\s+", "", match.group(1)).upper()
