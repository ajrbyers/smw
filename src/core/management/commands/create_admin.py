from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core import models

class Command(BaseCommand):
    help = "Run settings_import to sync settings and setting groups."

    def handle(self, *args, **options):

        username = password = 'admin'
        user = User.objects.create(
            username=username,
            email='admin@admin.com',
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        user.set_password(password)
        user.save()

        editor_role = models.Role.objects.get(slug='press-editor')

        profile = models.Profile.objects.create(
            user=user,
            country='gb',
            institution='Admin University'
        )
        profile.roles.add(editor_role)
        profile.save()

        print 'created user %r with password %r' % (username, password)
