# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0153_auto_20170712_1318'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='chapterauthor',
            unique_together=set([('chapter', 'first_name', 'middle_name', 'last_name')]),
        ),
    ]
