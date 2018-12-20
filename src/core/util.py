from bs4 import BeautifulSoup
from urllib.parse import quote

from core import models


def get_setting(setting_name, setting_group_name, default=None):
    try:
        setting = models.Setting.objects.get(
            name=setting_name,
            group__name=setting_group_name,
        )
        return setting.value
    except models.Setting.DoesNotExist:
        if default:
            return default
        return ''


def strip_html_tags(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text()


def add_content_disposition_header(
        response,
        filename,
        disposition='attachment'
):
    """
    Add an RFC5987 / RFC6266 compliant Content-Disposition header to an
    HttpResponse to tell the browser to save the HTTP response to a file.
    Args:
        response (django.http.response.HttpResponseBase): the response object.
        filename (str): the name that the file should be served under.
        disposition (str): the disposition: 'inline' or 'attachment' (default)

    """
    try:
        filename.encode('ascii')
        file_expr = 'filename="{}"'.format(filename)
    except UnicodeEncodeError:
        file_expr = "filename*=utf-8''{}".format(quote(filename))
    response['Content-Disposition'] = f'{disposition}; {file_expr}'
    return response
