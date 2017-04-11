# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0116_auto_20160421_0849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='book',
        ),
    ]
