# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0007_proposalreview_hide_details'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposalreview',
            old_name='hide_details',
            new_name='blind',
        ),
    ]
