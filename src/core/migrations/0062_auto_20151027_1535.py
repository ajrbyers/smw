# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_auto_20151027_1516'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={},
        ),
        migrations.RemoveField(
            model_name='role',
            name='required',
        ),
        migrations.RemoveField(
            model_name='role',
            name='sequence',
        ),
    ]
