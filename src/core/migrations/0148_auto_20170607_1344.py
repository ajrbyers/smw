# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0148_auto_20170519_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='peer_review_override',
            field=models.BooleanField(default=False, help_text=b'If enabled, this will mark a book as Peer Reviewed even if there are no reviews in the Rua database.'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/vhosts/rua_deploy/iitkship/src/media'), null=True, upload_to=core.models.profile_images_upload_path, blank=True),
        ),
    ]
