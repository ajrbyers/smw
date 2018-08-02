# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('editorialreview', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='editorialreview',
            name='assigning_editor',
            field=models.ForeignKey(related_name='editorial_review_assignments', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
