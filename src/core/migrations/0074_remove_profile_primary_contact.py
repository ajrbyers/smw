# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_profile_primary_contact'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='primary_contact',
        ),
    ]
