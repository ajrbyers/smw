# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0015_incompleteproposal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='date_accepted',
        ),
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='date_review_started',
        ),
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='date_submitted',
        ),
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='requestor',
        ),
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='review_assignments',
        ),
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='review_form',
        ),
        migrations.RemoveField(
            model_name='incompleteproposal',
            name='revision_due_date',
        ),
    ]
