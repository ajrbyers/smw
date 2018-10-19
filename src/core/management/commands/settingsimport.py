import os
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from core import models

def sync_groups():
    file = os.path.join(settings.BASE_DIR, 'core/fixtures/settinggroups.json')

    with open(file) as json_data:
        default_data = json.load(json_data)

        for entry in default_data:
            defaults = {
                'name': entry['fields'].get('name'),
                'enabled': entry['fields'].get('enabled'),
            }

            setting_group, created = models.SettingGroup.objects.get_or_create(
                id=entry['pk'],
                defaults=defaults
            )

            if created:
                print('Created setting group {0}'.format(setting_group.name))


def sync_settings():
    file = os.path.join(settings.BASE_DIR, 'core/fixtures/settings/master.json')

    with open(file) as json_data:
        default_data = json.load(json_data)

        for entry in default_data:
            group = models.SettingGroup.objects.get(id=int(entry['fields'].get('group')))

            defaults = {
                'group': group,
                'types': entry['fields'].get('types'),
                'value': entry['fields'].get('value'),
                'description': entry['fields'].get('description')
            }

            setting, created = models.Setting.objects.get_or_create(
                name=entry['fields'].get('name'),
                defaults=defaults
            )

            if created:
                print('Created setting {0}'.format(setting.name))


class Command(BaseCommand):

    help = "Run settings_import to sync settings and setting groups."

    def handle(self, *args, **options):
        sync_groups()
        sync_settings()
