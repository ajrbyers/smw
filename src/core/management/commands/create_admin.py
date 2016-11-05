import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User

from core import models

class Command(BaseCommand):

    help = "Run settings_import to sync settings and setting groups."

    def handle(self, *args, **options):

        user = User.objects.create(
            username='admin',
            email='admin@admin.com',
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )

        user.set_password('admin')

        user.save()

        editor_role = models.Role.objects.get(slug='press-editor')

        profile = models.Profile.objects.create(
            user=user,
            country='gb',
            institution='Admin University'
        )

        profile.roles.add(editor_role)

        profile.save()
