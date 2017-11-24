# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_auto_20171019_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='competing_interests',
            field=models.TextField(help_text=b"If any there are any competing interests please add them here. E.g.. 'This study was paid for by corp xyz.'. <a href='/page/competing_interests/'>More info</a>", null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(help_text=b'This is used for metadata,the website text and the back cover of the book', max_length=5000, null=True, verbose_name=b'Abstract', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='peer_review_override',
            field=models.BooleanField(default=False, help_text=(b'If enabled,this will mark a book as Peer Reviewed even if there are no reviews in the Rua database.',)),
        ),
        migrations.AlterField(
            model_name='book',
            name='table_contents_linked',
            field=models.BooleanField(default=False, help_text=b'If enabled,will make chapters on table of contents link to individual chapter pages.', verbose_name=b'Table of contents linked'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/vhosts/rua_deploy/template/src/media'), null=True, upload_to=core.models.profile_images_upload_path, blank=True),
        ),
        migrations.AlterField(
            model_name='retailer',
            name='link',
            field=models.URLField(help_text=b'FQDN of the book on the retailer website e.g. http://www.amazon.co.uk/mybook/', max_length=2000),
        ),
        migrations.AlterField(
            model_name='retailer',
            name='name',
            field=models.CharField(help_text=b'Name of retailer, E.g. Amazon or Book Depository', max_length=300),
        ),
        migrations.AddField(
            model_name='book',
            name='editorial_review_files',
            field=models.ManyToManyField(related_name='editorial_review_files', null=True, to='core.File', blank=True),
        ),
    ]
