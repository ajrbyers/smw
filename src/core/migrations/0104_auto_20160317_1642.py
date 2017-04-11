# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0103_book_editorial_review_assignments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='editorialreviewassignment',
            name='accepted',
        ),
        migrations.RemoveField(
            model_name='editorialreviewassignment',
            name='declined',
        ),
    ]
