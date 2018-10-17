# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_type', models.CharField(max_length=20, choices=[(b'editorial_group', b'Editorial Group'), (b'review_committee', b'Review Committee'), (b'generic', b'Generic')])),
                ('name', models.CharField(max_length=200)),
                ('active', models.BooleanField(default=True)),
                ('sequence', models.IntegerField()),
            ],
            options={
                'ordering': ('sequence', 'name'),
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateField(auto_now=True)),
                ('sequence', models.IntegerField()),
                ('group', models.ForeignKey(to='manager.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('sequence', 'added'),
            },
        ),
    ]
