# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0164_auto_20180608_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='series',
            name='handle',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
