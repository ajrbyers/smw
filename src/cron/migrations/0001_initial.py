# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CronTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('enabled', models.BooleanField(default=True)),
                ('schedule', models.CharField(max_length=20, choices=[(b'hourly', b'Hourly'), (b'daily', b'Daily'), (b'weekly', b'Weekly')])),
                ('note', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
