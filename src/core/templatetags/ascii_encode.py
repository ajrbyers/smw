from django import template

register = template.Library()

@register.filter
def ascii_encode(string):
    """ ASCII-encode a string, ignoring non-ASCII chars. """
    return string.encode('ascii', 'ignore')
