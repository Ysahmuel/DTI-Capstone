from django import template
from django.forms.widgets import Textarea
from decimal import Decimal
from django.utils.safestring import mark_safe

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
        display_method = getattr(obj, f"get_{attr_name}_display", None)
        if callable(display_method):
            display_value = display_method()
            return display_value if display_value not in [None, ""] else "-"

        value = getattr(obj, attr_name, None)

        # If callable
        if callable(value):
            return value()

        # Boolean field icons
        if isinstance(value, bool):
            icon_html = '<i class="fa-solid fa-square-check"></i>' if value else '<i class="fa-solid fa-square-xmark"></i>'
            return mark_safe(icon_html)

        # Integers
        if isinstance(value, int):
            return value or 0

        # Decimals / floats
        if isinstance(value, (Decimal, float)):
            return value or 0

        # Default
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