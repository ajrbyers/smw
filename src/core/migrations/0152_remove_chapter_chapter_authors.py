# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0151_chapter_chapter_authors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chapter',
            name='chapter_authors',
        ),
    ]
