# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_format'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('indentifier', models.CharField(max_length=200)),
                ('book', models.ForeignKey(to='core.Book')),
                ('file', models.ForeignKey(to='core.File')),
            ],
        ),
    ]
