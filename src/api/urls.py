from django.conf.urls import patterns, include, url

from rest_framework import routers

from api import views


router = routers.DefaultRouter()
router.register(r'jura', views.JuraBookViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', 'api.views.index', name='index'),
    url(r'^', include(router.urls)),
)
