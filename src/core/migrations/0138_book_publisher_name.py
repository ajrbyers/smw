# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0137_auto_20160808_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='publisher_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
