# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_auto_20171019_1554'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='editorial_review_files',
        ),
    ]
