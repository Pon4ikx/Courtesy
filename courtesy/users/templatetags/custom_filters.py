from django import template

register = template.Library()

@register.filter
def to(value, arg):
    return range(value, arg + 1)
