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
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes_from_editor', models.TextField(help_text=b'These notes should be as clear as possible to instruct the author on the revisions required. The notes will be displayed to the author.')),
                ('cover_letter', models.TextField(null=True, blank=True)),
                ('revision_type', models.CharField(max_length=100, choices=[(b'submission', b'Submission'), (b'review', b'Review')])),
                ('requested', models.DateField(auto_now_add=True)),
                ('due', models.DateField(help_text=b'Set the date the revisions are due. The author will be reminded once before the due date and once after.', null=True, blank=True)),
                ('completed', models.DateField(null=True, blank=True)),
                ('overdue_reminder', models.BooleanField(default=False)),
                ('book', models.ForeignKey(to='core.Book')),
                ('requestor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
