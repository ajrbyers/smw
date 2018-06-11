# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0030_proposalreview_access_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalreview',
            name='comments_from_editor',
            field=models.TextField(null=True, blank=True),
        ),
    ]
