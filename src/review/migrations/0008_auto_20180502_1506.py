# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0007_auto_20180323_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='ref',
            field=models.CharField(help_text=b'for proposals: press_code-proposal eg. sup-proposal', max_length=50),
        ),
    ]
