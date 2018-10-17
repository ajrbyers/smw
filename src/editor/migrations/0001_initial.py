# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoverImageProof',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assigned', models.DateField(auto_now_add=True)),
                ('note_to_author', models.TextField(help_text=b'Provide some notes on the cover for the author.')),
                ('completed', models.DateField(null=True, blank=True)),
                ('note_to_editor', models.TextField(help_text=b'Provide some feedback to the Editor on the cover image.')),
                ('book', models.ForeignKey(to='core.Book')),
                ('editor', models.ForeignKey(verbose_name=b'editor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
