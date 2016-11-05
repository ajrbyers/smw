# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='press_editors',
        ),
    ]
