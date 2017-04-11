# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0112_auto_20160412_1535'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='editorialreviewassignment',
            unique_together=set([]),
        ),
    ]
