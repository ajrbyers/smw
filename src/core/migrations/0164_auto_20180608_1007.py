# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import core.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0163_auto_20180323_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='handle',
            field=models.UUIDField(default=uuid.uuid4, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage(location=b'/Users/simoncrowe/PycharmProjects/rua/src/media'), null=True, upload_to=core.models.profile_images_upload_path, blank=True),
        ),
        migrations.AlterField(
            model_name='proposalform',
            name='ref',
            field=models.CharField(help_text=b'for proposals: press_code-proposal eg. sup-proposal', max_length=50),
        ),
    ]
