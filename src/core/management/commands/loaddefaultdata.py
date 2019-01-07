import json
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from core.models import (
    Language,
    License,
    Role,
    Setting,
    SettingGroup,
    ProposalForm,
    ProposalFormElement,
)
import review.models as review_models
from submission.models import SubmissionChecklistItem

LICENCE_FIXTURE = 'cc-licenses.json'


class Command(BaseCommand):
    """Loads core data necessary for proper running of a new Rua instance.
    Before data is loaded from JSON fixtures,
    """
    help = (
        "Run 'python manage.py initialise_default_data to load all default "
        "settings, setting-group, role, languages licence and form data."
    )

    def handle(self, *args, **options):
        # Loading of further fixtures is contingent on the success of the first
        # This reduces the number of database queries once data is loaded,
        # but also solved a problem when migrating Rua to k8s on 2019-01-07.
        if self.try_load_fixture_data('cc-licenses.json', License):
            self.try_load_fixture_data('langs.json', Language)
            self.try_load_fixture_data('role.json', Role)
            self.try_load_fixture_data('settinggroups.json', SettingGroup)
            self.try_load_fixture_data('settings/master.json', Setting)
            self.try_load_fixture_data(
                'forms/proposalformelement.json',
                ProposalFormElement,
            )
            self.try_load_fixture_data(
                'forms/proposalform_and_element_relationship.json',
                ProposalForm,
                fixture_model='core.proposalform',
            )
            self.try_load_fixture_data(
                'forms/review_formelement.json',
                review_models.FormElement,
            )
            self.try_load_fixture_data(
                'forms/review_form_and_element_relationship.json',
                review_models.Form,
                fixture_model='review.formelementsrelationship'
            )
            self.try_load_fixture_data(
                'forms/submissionchecklistitem.json',
                SubmissionChecklistItem,
            )

    @staticmethod
    def try_load_fixture_data(
            fixture_name,
            model_class,
            fixture_model=None
    ):
        fixtures = json.load(
            open(
                os.path.join(
                    settings.BASE_DIR,
                    'core',
                    'fixtures',
                    fixture_name
                )
            )
        )

        if fixture_model:
            primary_keys = [
                fixture['pk'] for fixture in fixtures
                if fixture['model'] == fixture_model
            ]
        else:
            primary_keys = [
                fixture['pk'] for fixture in fixtures
            ]

        if not model_class.objects.filter(pk__in=primary_keys):
            call_command('loaddata', fixture_name)
            return True
        else:
            print(
                f'Fixture {fixture_name} not loaded. One or more primary keys '
                'listed is already present in database.'
            )
