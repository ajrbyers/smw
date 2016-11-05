# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0117_remove_contract_book'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='proposal',
        ),
    ]
