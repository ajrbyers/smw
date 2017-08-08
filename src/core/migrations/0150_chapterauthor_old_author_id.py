# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0149_chapterauthor'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapterauthor',
            name='old_author_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
