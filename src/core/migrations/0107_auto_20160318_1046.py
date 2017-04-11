# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0106_auto_20160318_1045'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='editorialreviewassignment',
            unique_together=set([('book', 'management_editor', 'due')]),
        ),
    ]
