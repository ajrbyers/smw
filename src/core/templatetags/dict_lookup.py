from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import linebreaksbr
register = template.Library()

import json
import os

@register.simple_tag
def lookup(the_dict, key):
    # Try to fetch from the dict, and if it's not found return an empty string.
    the_dict = json.loads(the_dict)
    if the_dict.get(key, '')[1] == 'upload':
        url = reverse('proposals:serve_file', kwargs={'filename': os.path.basename(the_dict.get(key, '')[0])})
        return '<a href="%s">Download File</a>' % url
    else:
        return linebreaksbr(the_dict.get(key, '')[0])
