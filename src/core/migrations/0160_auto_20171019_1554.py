# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import models, migrations
import django.core.files.storage
import core.models

code = os.path.dirname(os.path.dirname(__file__)).split('/')[-2]
MEDIA_ROOT = '/var/www/vhosts/rua_deploy/{code}/src/media'.format(
    code=code
)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0159_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='table_contents_linked',
            field=models.BooleanField(default=False, help_text=b'If enabled, will make chapters on table of contents link to individual chapter pages.', verbose_name=b'Table of contents linked'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage(location=MEDIA_ROOT), null=True, upload_to=core.models.profile_images_upload_path, blank=True),
        ),
    ]
