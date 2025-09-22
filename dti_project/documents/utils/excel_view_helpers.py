
def to_title(value):
    """Normalize strings: remove underscores, title-case, handle non-strings gracefully."""
    if not isinstance(value, str):
        return value
    return value.replace("_", " ").title()

def normalize_sheet_name(name: str) -> str:
    """Convert sheet name like 'Sales Promotion Permit Applications' 
    into a lookup key matching EXPORT_MODEL_MAP keys."""
    return name.lower().replace(" ", "").rstrip("s")