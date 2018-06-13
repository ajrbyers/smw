# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0165_auto_20180608_1010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='series',
            old_name='name',
            new_name='title',
        ),
    ]
