# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0154_auto_20170712_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapterauthor',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterUniqueTogether(
            name='chapterauthor',
            unique_together=set([('chapter', 'uuid')]),
        ),
    ]
