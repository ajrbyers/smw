from __future__ import unicode_literals
import os

from celery import Celery

from django.conf import settings


# Point Django settings env variable to core.settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(settings.INSTALLED_APPS)
