# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_typesetassignment_note_to_typesetter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='typesetassignment',
            old_name='typsetter_invited',
            new_name='typesetter_invited',
        ),
    ]
