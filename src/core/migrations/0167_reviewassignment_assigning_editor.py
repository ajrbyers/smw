# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0166_auto_20180612_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewassignment',
            name='assigning_editor',
            field=models.ForeignKey(related_name='review_assignments', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
