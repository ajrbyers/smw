from __future__ import print_function

from django.conf import settings

from nameko.events import EventDispatcher
from nameko.rpc import rpc


class ServiceHandler(object):

    def __init__(self, service):
        self.service = service

    def send(self, content):
        """ Send content over RPC to a service, triggering pre and post actions.

        Args:
            content (object): Content to send over RPC to connected service.
        """

        try:
            with settings.CLUSTER_RPC as cluster_rpc:
                running_service = getattr(cluster_rpc, self.service.name)
                running_service.send(content)
        except Exception as e:
            print(e)


class JuraUpdateService(object):
    """ Nameko class to update Jura."""

    name = 'jura_update_service'
    dispatch = EventDispatcher()

    @rpc
    def send(self, book_id):
        self.dispatch('rua_update', book_id)
