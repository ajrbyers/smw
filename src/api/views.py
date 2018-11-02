import json

from django.http import HttpResponse
from django.utils.encoding import smart_text

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

from api import serializers
from core.models import Book


class JSONResponse(HttpResponse):
    """ An HttpResponse that renders its content into JSON. """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def index(request):
    response_dict = {
        'Message': 'Welcome to the API',
        'Version': '1.0',
        'API Endpoints':
            [],
    }
    json_content = smart_text(json.dumps(response_dict))

    return HttpResponse(json_content, content_type="application/json")


class JuraBookViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    queryset = Book.objects.all().order_by('id')
    serializer_class = serializers.JuraBookSerializer
