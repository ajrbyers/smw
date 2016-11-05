# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0004_auto_20160120_1636'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formelementsrelationship',
            old_name='element_class',
            new_name='width',
        ),
    ]
