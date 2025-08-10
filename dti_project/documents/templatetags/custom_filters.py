from django import template
from django.forms.widgets import Textarea
from decimal import Decimal

register = template.Library()

@register.filter
def titlecase(value):
    return str(value).replace('_', ' ').title()

@register.filter
def get_form_field(form, field_name):
    """Safely get a field from a Django form by name"""
    return form[field_name]

@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, Textarea)

@register.filter()
def get_attr(obj, attr_name):
    try:
        value = getattr(obj, attr_name, None)

        # If callable (e.g., get_<field>_display), call it
        if callable(value):
            return value()

        # If it's an int and None/falsy, return 0
        if isinstance(value, int):
            return value or 0

        # If it's a Decimal or float, same logic
        if isinstance(value, (Decimal, float)):
            return value or 0

        # Default: return value or '-'
        return value if value not in [None, ""] else "-"
    except Exception:
        return "-"

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def dash_if_empty(value):
    """Return '-' if value is None, empty, or only whitespace."""
    if value is None or str(value).strip() == "":
        return "-"
    return value