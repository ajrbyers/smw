# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryProposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.IntegerField(default=1)),
                ('title', models.CharField(max_length=255, verbose_name=b'Book Title')),
                ('subtitle', models.CharField(max_length=255, null=True, blank=True)),
                ('author', models.CharField(max_length=255, verbose_name=b'Submitting author/editor')),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField(null=True, blank=True)),
                ('date_review_started', models.DateTimeField(null=True, blank=True)),
                ('revision_due_date', models.DateTimeField(null=True, blank=True)),
                ('date_accepted', models.DateTimeField(null=True, blank=True)),
                ('date_edited', models.DateTimeField(null=True, blank=True)),
                ('book_type', models.CharField(blank=True, max_length=50, null=True, help_text=b'A monograph is a work authored, in its entirety, by one or more authors. An edited volume has different authors for each chapter.', choices=[(b'monograph', b'Monograph'), (b'edited_volume', b'Edited Volume')])),
                ('status', models.CharField(default=b'submission', max_length=20, choices=[(b'submission', b'Submission'), (b'revisions_required', b'Revisions Required'), (b'revisions_submitted', b'Revisions Submitted'), (b'accepted', b'Accepted'), (b'declined', b'Declined')])),
                ('form', models.ForeignKey(related_name='parent_proposal_Form', to='core.ProposalForm')),
                ('owner', models.ForeignKey(related_name='parent_proposal_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncompleteProposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, verbose_name=b'Book Title', blank=True)),
                ('subtitle', models.CharField(max_length=255, null=True, blank=True)),
                ('author', models.CharField(max_length=255, null=True, verbose_name=b'Submitting author/editor', blank=True)),
                ('data', models.TextField(null=True, blank=True)),
                ('book_type', models.CharField(blank=True, max_length=50, null=True, help_text=b'A monograph is a work authored, in its entirety, by one or more authors. An edited volume has different authors for each chapter.', choices=[(b'monograph', b'Monograph'), (b'edited_volume', b'Edited Volume')])),
                ('status', models.CharField(default=b'submission', max_length=20, null=True, blank=True, choices=[(b'submission', b'Submission'), (b'revisions_required', b'Revisions Required'), (b'revisions_submitted', b'Revisions Submitted'), (b'accepted', b'Accepted'), (b'declined', b'Declined')])),
                ('form', models.ForeignKey(blank=True, to='core.ProposalForm', null=True)),
                ('owner', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Book Title')),
                ('subtitle', models.CharField(max_length=255, null=True, blank=True)),
                ('author', models.CharField(max_length=255, verbose_name=b'Submitting author/editor')),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField(null=True, blank=True)),
                ('date_review_started', models.DateTimeField(null=True, blank=True)),
                ('revision_due_date', models.DateTimeField(null=True, blank=True)),
                ('date_accepted', models.DateTimeField(null=True, blank=True)),
                ('book_type', models.CharField(blank=True, max_length=50, null=True, help_text=b'A monograph is a work authored, in its entirety, by one or more authors. An edited volume has different authors for each chapter.', choices=[(b'monograph', b'Monograph'), (b'edited_volume', b'Edited Volume')])),
                ('current_version', models.IntegerField(default=1)),
                ('status', models.CharField(default=b'submission', max_length=20, choices=[(b'submission', b'Submission'), (b'revisions_required', b'Revisions Required'), (b'revisions_submitted', b'Revisions Submitted'), (b'accepted', b'Accepted'), (b'declined', b'Declined')])),
                ('book_editors', models.ManyToManyField(related_name='proposal_book_editors', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('contract', models.ForeignKey(related_name='contract_of_proposal', blank=True, to='core.Contract', null=True)),
                ('form', models.ForeignKey(to='core.ProposalForm')),
                ('owner', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('requestor', models.ForeignKey(related_name='editor_requestor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProposalNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
                ('date_last_updated', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('proposal', models.ForeignKey(to='submission.Proposal')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProposalReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assigned', models.DateField(auto_now_add=True)),
                ('accepted', models.DateField(null=True, blank=True)),
                ('declined', models.DateField(null=True, blank=True)),
                ('due', models.DateField(null=True, blank=True)),
                ('completed', models.DateField(null=True, blank=True)),
                ('recommendation', models.CharField(blank=True, max_length=10, null=True, choices=[(b'accept', b'Accept'), (b'reject', b'Reject'), (b'revisions', b'Revisions Required')])),
                ('competing_interests', models.TextField(help_text=b"If any of the authors or editors have any competing interests please add them here. e.g.. 'This study was paid for by corp xyz.'", null=True, blank=True)),
                ('blind', models.NullBooleanField(default=False)),
                ('access_key', models.CharField(max_length=200, null=True, blank=True)),
                ('hide', models.BooleanField(default=False)),
                ('comments_from_editor', models.TextField(null=True, blank=True)),
                ('reopened', models.BooleanField(default=False)),
                ('withdrawn', models.BooleanField(default=False)),
                ('files', models.ManyToManyField(to='core.File', null=True, blank=True)),
                ('proposal', models.ForeignKey(to='submission.Proposal')),
                ('requestor', models.ForeignKey(related_name='review_requestor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('results', models.ForeignKey(blank=True, to='review.FormResult', null=True)),
                ('review_form', models.ForeignKey(blank=True, to='review.Form', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionChecklistItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=500)),
                ('sequence', models.IntegerField(default=999)),
                ('required', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('sequence', 'text'),
            },
        ),
        migrations.AddField(
            model_name='proposal',
            name='review_assignments',
            field=models.ManyToManyField(related_name='review', null=True, to='submission.ProposalReview', blank=True),
        ),
        migrations.AddField(
            model_name='proposal',
            name='review_form',
            field=models.ForeignKey(blank=True, to='review.Form', null=True),
        ),
        migrations.AddField(
            model_name='historyproposal',
            name='proposal',
            field=models.ForeignKey(related_name='parent_proposal', to='submission.Proposal'),
        ),
        migrations.AddField(
            model_name='historyproposal',
            name='requestor',
            field=models.ForeignKey(related_name='parent_proposal_Requestor', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historyproposal',
            name='review_form',
            field=models.ForeignKey(blank=True, to='review.Form', null=True),
        ),
        migrations.AddField(
            model_name='historyproposal',
            name='user_edited',
            field=models.ForeignKey(related_name='edited_by_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='proposalreview',
            unique_together=set([('proposal', 'user')]),
        ),
    ]
