from django.urls import (
    include,
    re_path,
)

from rest_framework import routers

from api.views import (
    index,
    JuraBookViewSet,
)

router = routers.DefaultRouter()
router.register(r'jura', JuraBookViewSet)

urlpatterns = [
    re_path(r'^$', index, name='index'),
    re_path(r'^', include(router.urls)),
]
