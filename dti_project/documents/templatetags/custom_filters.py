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