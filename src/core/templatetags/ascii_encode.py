from django import template

register = template.Library()

@register.filter
def ascii_encode(string):
    """ ASCII-encode a string, replacing non-ASCII chars with HTML elements. """
    return string.encode('ascii', 'xmlcharrefreplace')
