# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0157_auto_20170712_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='table_contents',
        ),
        migrations.AddField(
            model_name='book',
            name='table_contents_linked',
            field=models.BooleanField(default=False, help_text=b'If enabled, will make chapters on table of contents linkto individual chapter pages.'),
        ),
    ]
