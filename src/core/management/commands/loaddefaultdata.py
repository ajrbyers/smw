from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Run 'python manage.py initilise_default_data to load all default "
        "settings, setting-group, role, languages licence and form data."
    )

    def handle(self, *args, **options):
        call_command('loaddata', 'cc-licenses.json')
        call_command('loaddata', 'langs.json')
        call_command('loaddata', 'role.json')
        call_command('loaddata', 'settinggroups.json')
        call_command('loaddata', 'settings/master.json')
        call_command('loaddata', 'forms/master.json')
