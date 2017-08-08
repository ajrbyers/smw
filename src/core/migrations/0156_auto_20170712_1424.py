# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0155_auto_20170712_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapterauthor',
            name='uuid',
            field=models.UUIDField(default=b'd4c2dfbd20f7408194e77a03648a13e2', editable=False),
        ),
    ]
