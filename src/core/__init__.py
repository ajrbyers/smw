from __future__ import absolute_import, unicode_literals

from .celery import app as celery_app

# Make sure that Celery app is always imported when Django starts
__all__ = ['celery_app']
