# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20181017_1003'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditorialReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('assigned', models.DateField(auto_now_add=True)),
                ('due', models.DateField(null=True, blank=True)),
                ('completed', models.DateField(null=True, blank=True)),
                ('body', models.TextField(null=True, blank=True)),
                ('access_key', models.CharField(max_length=200, null=True, blank=True)),
                ('recommendation', models.CharField(blank=True, max_length=10, null=True, choices=[(b'accept', b'Accept'), (b'reject', b'Reject'), (b'revisions', b'Revisions Required')])),
                ('competing_interests', models.TextField(help_text=b"If any of the authors or editors have any competing interests please add them here. e.g.. 'This study was paid for by corp xyz.'. <a href='/page/competing_interests/'>More info</a>", null=True, blank=True)),
                ('overdue_reminder', models.BooleanField(default=False)),
                ('reopened', models.BooleanField(default=False)),
                ('withdrawn', models.BooleanField(default=False)),
                ('assigning_editor', models.ForeignKey(related_name='editorial_review_assignments', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('files', models.ManyToManyField(to='core.File', null=True, blank=True)),
                ('results', models.ForeignKey(blank=True, to='review.FormResult', null=True)),
                ('review_form', models.ForeignKey(blank=True, to='review.Form', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
