from django.conf.urls import (
    include,
    url,
)

from rest_framework import routers

from api.views import (
    index,
    JuraBookViewSet,
)

router = routers.DefaultRouter()
router.register(r'jura', JuraBookViewSet)

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^', include(router.urls)),
]
