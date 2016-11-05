from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'jura', views.JuraBookViewSet)
router.register(r'omp', views.OMPViewSet)
router.register(r'license', views.LicenseViewSet)

urlpatterns = patterns('',
                       url(r'^$', 'api.views.index', name='index'),
                       url(r'^', include(router.urls)),
                       )
