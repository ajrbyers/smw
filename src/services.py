from __future__ import print_function

from django.conf import settings

from nameko.events import EventDispatcher
from nameko.rpc import rpc


class ServiceHandler(object):

    def __init__(self, service):
        self.service = service

    def send(self, content):
        """Send content over RPC to a service, triggering pre and post actions.

        Args:
            content (object): Content to send over RPC to connected service.
        """
        prepared_content = self.service.pre_send(content)

        try:
            with settings.CLUSTER_RPC as cluster_rpc:
                running_service = getattr(cluster_rpc, self.service.name)
                running_service.send(prepared_content)
        except Exception as e:
            print(e)


class JuraUpdateService(object):
    """Nameko class to update Jura."""

    name = 'jura_update_service'
    dispatch = EventDispatcher()

    @staticmethod
    def pre_send(book_id):
        """Serialise book ID with cleaned press URL for Jura scrape."""

        press_rua_url = settings.BASE_URL.rstrip('/')

        if 'https://' in press_rua_url:
            press_rua_url = press_rua_url.replace('https://', '')
        elif 'http://' in press_rua_url:
            press_rua_url = press_rua_url.replace('http://', '')

        book_dict = {
            'rua_book_id': book_id,
            'press_rua_url': press_rua_url
        }

        return book_dict

    @rpc
    def send(self, book_dict):
        self.dispatch('rua_update', book_dict)
