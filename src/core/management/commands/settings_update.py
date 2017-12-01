import os
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from core import models


class Command(BaseCommand):
    help = "Run 'python manage.py settings_update <setting_name>' to update or create the specified setting model from master.json."

    def add_arguments(self, parser):
        parser.add_argument('setting_name')

    def handle(self, *args, **options):
        file = os.path.join(settings.BASE_DIR, 'core/fixtures/settings/master.json')

        with open(file) as json_data:
            default_data = json.load(json_data)

            for setting in default_data:
                if setting['fields']['name'] == options['setting_name']:

                    group = models.SettingGroup.objects.get(pk=int(setting['fields']['group']))
                    defaults = {
                        'types': setting['fields']['types'],
                        'value': setting['fields']['value'],
                        'description': setting['fields']['description'],
                        'group': group,
                    }

                    s, created = models.Setting.objects.update_or_create(
                        name=setting['fields']['name'],
                        defaults=defaults
                    )

                    if created:
                        print 'Created setting {}'.format(s.name)
                    else:
                        print 'Updated setting {}'.format(s.name)

                elif not any(setting['fields']['name'] == options['setting_name'] for setting in default_data):
                    print 'Setting {0} not found.'.format(options['setting_name'])
