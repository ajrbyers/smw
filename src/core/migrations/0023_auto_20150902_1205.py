# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20150902_0916'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='publicaton_date',
            new_name='publication_date',
        ),
    ]
