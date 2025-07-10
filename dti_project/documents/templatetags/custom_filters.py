from django import template

register = template.Library()

@register.filter
def titlecase(value):
    return str(value).replace('_', ' ').title()