# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0152_remove_chapter_chapter_authors'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='chapterauthor',
            unique_together=set([('chapter', 'author_email')]),
        ),
    ]
