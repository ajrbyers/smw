# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20150606_2132'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('sequence', 'name')},
        ),
        migrations.AlterModelOptions(
            name='groupmembership',
            options={'ordering': ('sequence', 'added')},
        ),
    ]
