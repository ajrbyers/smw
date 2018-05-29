from django import template

from core import logic

register = template.Library()


@register.filter
def ascii_encode(string):
    """ ASCII-encode a string, replacing non-ASCII chars with HTML elements. """
    return logic.ascii_encode(string)
