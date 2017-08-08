# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0156_auto_20170712_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapterauthor',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterUniqueTogether(
            name='chapterauthor',
            unique_together=set([]),
        ),
    ]
