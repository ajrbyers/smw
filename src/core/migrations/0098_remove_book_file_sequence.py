# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_book_file_sequence'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='file_sequence',
        ),
    ]
