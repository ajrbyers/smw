# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0162_auto_20171201_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalform',
            name='active',
            field=models.BooleanField(default=True, help_text=b'If set to False, will be hidden from use in proposal workflow.'),
        ),
        migrations.AddField(
            model_name='proposalform',
            name='in_edit',
            field=models.BooleanField(default=False, help_text=b'True if form is in edit stage.'),
        ),
        migrations.AlterField(
            model_name='proposalformelement',
            name='choices',
            field=models.CharField(help_text=b'Separate choices with the bar | character.', max_length=500, null=True, blank=True),
        ),
    ]
