# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('submission', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='proposal',
            field=models.ForeignKey(related_name='proposal_log', blank=True, to='submission.Proposal', null=True),
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='indexassignment',
            name='book',
            field=models.ForeignKey(to='core.Book'),
        ),
        migrations.AddField(
            model_name='indexassignment',
            name='files',
            field=models.ManyToManyField(to='core.File', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='indexassignment',
            name='index_files',
            field=models.ManyToManyField(related_name='index_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='indexassignment',
            name='indexer',
            field=models.ForeignKey(related_name='indexer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='indexassignment',
            name='requestor',
            field=models.ForeignKey(related_name='index_requestor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='identifier',
            name='book',
            field=models.ForeignKey(blank=True, to='core.Book', null=True),
        ),
        migrations.AddField(
            model_name='identifier',
            name='digital_format',
            field=models.ForeignKey(related_name='digital_format', blank=True, to='core.Format', null=True),
        ),
        migrations.AddField(
            model_name='identifier',
            name='physical_format',
            field=models.ForeignKey(blank=True, to='core.PhysicalFormat', null=True),
        ),
        migrations.AddField(
            model_name='format',
            name='book',
            field=models.ForeignKey(to='core.Book'),
        ),
        migrations.AddField(
            model_name='format',
            name='file',
            field=models.ForeignKey(to='core.File'),
        ),
        migrations.AddField(
            model_name='fileversion',
            name='file',
            field=models.ForeignKey(to='core.File'),
        ),
        migrations.AddField(
            model_name='fileversion',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='attachment',
            field=models.ManyToManyField(related_name='email_attachment', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='book',
            field=models.ForeignKey(blank=True, to='core.Book', null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='proposal',
            field=models.ForeignKey(blank=True, to='submission.Proposal', null=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='book',
            field=models.ForeignKey(to='core.Book'),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='editorial_board',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='editorial_board_files',
            field=models.ManyToManyField(related_name='editorial_board_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='editorial_board_results',
            field=models.ForeignKey(related_name='eb_review_form_results', blank=True, to='review.FormResult', null=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='editorial_board_review_form',
            field=models.ForeignKey(related_name='eb_review_form', blank=True, to='review.Form', null=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='management_editor',
            field=models.ForeignKey(related_name='management_editor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='publication_committee_files',
            field=models.ManyToManyField(related_name='publication_committee_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='publication_committee_results',
            field=models.ForeignKey(related_name='pc_review_form_results', blank=True, to='review.FormResult', null=True),
        ),
        migrations.AddField(
            model_name='editorialreviewassignment',
            name='publication_committee_review_form',
            field=models.ForeignKey(related_name='pc_review_form', blank=True, to='review.Form', null=True),
        ),
        migrations.AddField(
            model_name='copyeditassignment',
            name='author_files',
            field=models.ManyToManyField(related_name='author_copyedit_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='copyeditassignment',
            name='book',
            field=models.ForeignKey(to='core.Book'),
        ),
        migrations.AddField(
            model_name='copyeditassignment',
            name='copyedit_files',
            field=models.ManyToManyField(related_name='copyedit_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='copyeditassignment',
            name='copyeditor',
            field=models.ForeignKey(related_name='copyeditor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='copyeditassignment',
            name='files',
            field=models.ManyToManyField(related_name='cp_assigned_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='copyeditassignment',
            name='requestor',
            field=models.ForeignKey(related_name='copyedit_requestor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contract',
            name='author_file',
            field=models.ForeignKey(related_name='author_file', blank=True, to='core.File', null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='editor_file',
            field=models.ForeignKey(related_name='editor_file', blank=True, to='core.File', null=True),
        ),
        migrations.AddField(
            model_name='chapterformat',
            name='book',
            field=models.ForeignKey(to='core.Book'),
        ),
        migrations.AddField(
            model_name='chapterformat',
            name='chapter',
            field=models.ForeignKey(related_name='format_chapter', to='core.Chapter'),
        ),
        migrations.AddField(
            model_name='chapterformat',
            name='file',
            field=models.ForeignKey(to='core.File'),
        ),
        migrations.AddField(
            model_name='chapterauthor',
            name='chapter',
            field=models.ForeignKey(to='core.Chapter'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='authors',
            field=models.ManyToManyField(to='core.Author', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='book',
            field=models.ForeignKey(to='core.Book'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='disciplines',
            field=models.ManyToManyField(to='core.Subject', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='formats',
            field=models.ManyToManyField(related_name='formats', null=True, to='core.ChapterFormat', blank=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='keywords',
            field=models.ManyToManyField(to='core.Keyword', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.ManyToManyField(to='core.Author', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='book_editors',
            field=models.ManyToManyField(related_name='book_editors', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='contract',
            field=models.ForeignKey(related_name='contract_of_book', blank=True, to='core.Contract', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='editor',
            field=models.ManyToManyField(to='core.Editor', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='editorial_review_assignments',
            field=models.ManyToManyField(related_name='editorial_review', null=True, to='core.EditorialReviewAssignment', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='external_review_files',
            field=models.ManyToManyField(related_name='external_review_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='files',
            field=models.ManyToManyField(to='core.File', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='internal_review_files',
            field=models.ManyToManyField(related_name='internal_review_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='keywords',
            field=models.ManyToManyField(to='core.Keyword', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='languages',
            field=models.ManyToManyField(to='core.Language', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='license',
            field=models.ForeignKey(blank=True, to='core.License', help_text=b'The license you recommend for this work.', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='misc_files',
            field=models.ManyToManyField(related_name='misc_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='owner',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='press_editors',
            field=models.ManyToManyField(related_name='press_editors', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='production_editors',
            field=models.ManyToManyField(related_name='production_editors', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='production_files',
            field=models.ManyToManyField(related_name='production_files', null=True, to='core.File', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='proposal',
            field=models.ForeignKey(blank=True, to='submission.Proposal', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='read_only_users',
            field=models.ManyToManyField(related_name='read_only_users', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='review_assignments',
            field=models.ManyToManyField(related_name='review', null=True, to='core.ReviewAssignment', blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='review_form',
            field=models.ForeignKey(blank=True, to='review.Form', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='series',
            field=models.ForeignKey(blank=True, to='core.Series', help_text=b'If you are submitting this work to an existing Series please select it.', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='stage',
            field=models.ForeignKey(blank=True, to='core.Stage', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='subject',
            field=models.ManyToManyField(to='core.Subject', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='reviewround',
            unique_together=set([('book', 'round_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='reviewassignment',
            unique_together=set([('book', 'user', 'review_type', 'review_round')]),
        ),
    ]
