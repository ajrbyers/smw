# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from core import models as core_models

def update_setting(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    setting = core_models.Setting.objects.filter(name='proposal_review_request')
    if setting:
        value = setting[0].value
        value = value.replace('{{review.due}}', '_due_date_')
        value = value.replace('{{revision.due}}', '_due_date_')
        setting[0].value = value
        setting[0].save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0123_auto_20160429_1025'),
    ]

    operations = [
        migrations.RunPython(update_setting),
    ]
