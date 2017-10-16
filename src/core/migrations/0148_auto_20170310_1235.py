# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0147_auto_20161026_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='editorial_review_files',
            field=models.ManyToManyField(related_name='editorial_review_files', null=True, to='core.File', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='peer_review_override',
            field=models.BooleanField(default=False, help_text=b'If enabled, this will mark a book as Peer Reviewed even if there are no reviews in the Rua database.'),
        ),
    ]
