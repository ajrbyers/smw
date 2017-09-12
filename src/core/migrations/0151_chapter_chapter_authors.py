# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0150_chapterauthor_old_author_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='chapter_authors',
            field=models.ManyToManyField(related_name='chapter_authors', null=True, to='core.ChapterAuthor', blank=True),
        ),
    ]
