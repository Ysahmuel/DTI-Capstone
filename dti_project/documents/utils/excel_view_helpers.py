import re
from django.contrib.auth import get_user_model
from difflib import get_close_matches
from documents.mappings import UPLOAD_MODEL_MAP

def to_title(value):
    """Normalize strings: remove underscores, title-case, handle non-strings gracefully."""
    if not isinstance(value, str):
        return value
    return value.replace("_", " ").title()

def normalize_sheet_name(name: str) -> str:
    """Convert sheet name like 'Sales Promotion Permit Applications' 
    into a lookup key matching EXPORT_MODEL_MAP keys."""
    return name.lower().replace(" ", "").rstrip("s")

def normalize_header(h):
    """Normalize headers to match Django field names or verbose_names."""
    if not h:
        return ""
    return str(h).strip().lower().replace(" ", "_")

User = get_user_model()

def get_user_from_full_name(full_name: str):
    """
    Try to resolve a User by full name (first + last).
    Falls back gracefully if not found.
    """
    if not full_name:
        return None
    
    parts = full_name.strip().split()
    if len(parts) < 2:
        return None  # not enough info to split
    
    first_name, last_name = parts[0], parts[-1]
    try:
        return User.objects.get(first_name__iexact=first_name, last_name__iexact=last_name)
    except User.DoesNotExist:
        return None
    
def shorten_name(name, max_length=31):
    words = name.split()
    shortened = " ".join(words[:3])
    if len(shortened) > max_length:
        return shortened[:max_length]  
    return shortened
    
def get_model_from_sheet(sheetname):
    normalized = normalize_sheet_name(sheetname)
    candidates = list(UPLOAD_MODEL_MAP.keys())
    match = get_close_matches(normalized, candidates, n=1, cutoff=0.6)

    if match:
        return UPLOAD_MODEL_MAP[match[0]]
    return None