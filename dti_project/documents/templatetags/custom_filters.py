from django import template
from django.forms.widgets import Textarea

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

@register.filter(name='get_attr')
def get_attr(obj, attr_name):
    try:
        return getattr(obj, attr_name, '-') or '-'
    except Exception:
        return '-'

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def dash_if_empty(value):
    """Return '-' if value is None, empty, or only whitespace."""
    if value is None or str(value).strip() == "":
        return "-"
    return value