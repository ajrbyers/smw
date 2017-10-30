import json
from urllib import urlencode

from django.conf import settings

import requests

ORCID_API = settings.ORCID_API_URL
ORCID_REQ = '/orcid-profile'
R_HEADERS = {'Accept': 'application/orcid+json'}


def request_profile(orcid_id):
    url = '%s%s%s' % (ORCID_API, orcid_id, ORCID_REQ)
    request = requests.get(url, headers=R_HEADERS)
    if request.status_code == 200:
        _dict = json.loads(request.text)
        return parse_profile(_dict['orcid-profile'])
    return None


def dict_getter(_dict, path_list):
    to_return = _dict
    for path in path_list:
        try:
            to_return = to_return.get(path)
        except:
            to_return = None

    if to_return:
        return to_return
    return ''


def parse_profile(profile):
    first_name = dict_getter(
        profile,
        ['orcid-bio', 'personal-details', 'given-names', 'value']
    )
    last_name = dict_getter(
        profile,
        ['orcid-bio', 'personal-details', 'family-name', 'value']
    )
    country = dict_getter(
        profile,
        ['orcid-bio', 'contact-details', 'address', 'country', 'value']
    )

    try:
        inst = dict_getter(
            profile,
            ['orcid-activities', 'affiliations', 'affiliation']
        )[0]
    except IndexError:
        inst = ''

    bio = dict_getter(profile, ['orcid-bio', 'biography', 'value'])
    org_name = dict_getter(inst, ['organization', 'name'])
    city = dict_getter(inst, ['organization', 'address', 'city'])
    region = dict_getter(inst, ['organization', 'address', 'region'])
    department = dict_getter(inst, ['department-name'])
    orcid_id = dict_getter(profile, ['orcid-identifier', 'path'])

    return {
        'first_name': first_name,
        'last_name': last_name,
        'country': country,
        'department': department,
        'inst': '%s %s %s' % (org_name, city, region),
        'bio': bio,
        'orcid': orcid_id,
    }


def retrieve_tokens(authorization_code, domain=None):
    access_token_req = {
        "code": authorization_code,
        "client_id": settings.ORCID_CLIENT_ID,
        "client_secret": settings.ORCID_CLIENT_SECRET,
        "redirect_uri": 'http://%s/login/orcid/' % domain
        if domain else settings.ORCID_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    content_length = len(urlencode(access_token_req))
    access_token_req['content-length'] = str(content_length)
    base_url = settings.ORCID_TOKEN_URL

    r = requests.post(base_url, data=access_token_req)
    data = json.loads(r.text)

    return data
