from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from author import forms, logic
from core import models, log, task, logic as core_logic, forms as core_forms
from core.decorators import is_author
from core import email
from core.files import (
    handle_attachment,
    handle_file_update,
    handle_file,
    handle_multiple_email_files,
    handle_proposal_file,
    handle_typeset_file,
)
from core.logic import order_data, decode_json
from editor import models as editor_models
from review import models as review_models
from revisions import models as revision_models
from submission import models as submission_models, logic as submission_logic
from core.setting_util import get_setting


@is_author
def author_dashboard(request):
    direct_submissions = get_setting('direct_submissions', 'general')
    submit_proposals = get_setting('submit_proposals', 'general')

    template = 'author/dashboard.html'
    context = {
        'user_submissions': models.Book.objects.filter(
            owner=request.user
        ).order_by(
            '-pk'
        ).select_related(
            'stage'
        ),
        'user_proposals': submission_models.Proposal.objects.filter(
            owner=request.user
        ).order_by(
            '-pk'
        ),
        'user_incomplete_proposals':
            submission_models.IncompleteProposal.objects.filter(
                owner=request.user
            ).order_by(
                '-pk'
            ),
        'author_tasks': logic.author_tasks(request.user),
        'author_task_number': len(logic.author_tasks(request.user)),
        'new_messages': logic.check_for_new_messages(request.user),
        'direct_submissions': direct_submissions,
        'submit_proposals': submit_proposals,
    }

    return render(request, template, context)


@login_required
def author_submission(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    template = 'author/submission.html'
    context = {
        'submission': book,
        'active': 'user_submission',
        'author_include': 'author/submission_details.html',
        'submission_files': 'author/submission_files.html'
    }

    return render(request, template, context)


@login_required
def status(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    template = 'author/submission.html'
    context = {
        'submission': book,
        'active': 'user_submission',
        'author_include': 'shared/status.html',
        'submission_files': 'shared/messages.html',
        'timeline': core_logic.build_time_line(book),
    }

    return render(request, template, context)


@login_required
def review(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)

    review_rounds = models.ReviewRound.objects.filter(book=book).order_by(
        '-round_number')

    template = 'author/submission.html'
    context = {
        'submission': book,
        'author_include': 'author/review_revision.html',
        'review_rounds': review_rounds,
        'revision_requests': revision_models.Revision.objects.filter(
            book=book,
            revision_type='review'
        )
    }

    return render(request, template, context)


@login_required
def view_review_round(request, submission_id, round_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    review_round = get_object_or_404(
        models.ReviewRound,
        book=book,
        round_number=round_id,
    )
    models.ReviewAssignment.objects.filter(
        book=book,
        review_round__book=book,
        review_round__round_number=round_id,
    )

    review_rounds = models.ReviewRound.objects.filter(
        book=book
    ).order_by(
        '-round_number'
    )
    internal_review_assignments = models.ReviewAssignment.objects.filter(
        book=book,
        review_type='internal',
        review_round__round_number=round_id,
        hide=False,
    ).select_related(
        'user', 'review_round'
    )
    external_review_assignments = models.ReviewAssignment.objects.filter(
        book=book,
        review_type='external',
        review_round__round_number=round_id,
        hide=False
    ).select_related(
        'user', 'review_round'
    )

    template = 'author/submission.html'
    context = {
        'submission': book,
        'author_include': 'author/review_revision.html',
        'submission_files': 'author/view_review_round.html',
        'review_round': review_round,
        'review_rounds': review_rounds,
        'round_id': round_id,
        'revision_requests': revision_models.Revision.objects.filter(
            book=book,
            revision_type='review',
        ),
        'internal_review_assignments': internal_review_assignments,
        'external_review_assignments': external_review_assignments,
    }

    return render(request, template, context)


@login_required
def view_review_assignment(request, submission_id, round_id, review_id):
    submission = get_object_or_404(
        models.Book,
        pk=submission_id,
        owner=request.user,
    )
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    review_rounds = models.ReviewRound.objects.filter(
        book=submission
    ).order_by(
        '-round_number',
    )

    if review_assignment.hide:
        return redirect(reverse(
            'view_review_round',
            kwargs={'submission_id': submission_id, 'round_id': round_id})
        )

    result = review_assignment.results
    if result:
        relations = review_models.FormElementsRelationship.objects.filter(
            form=result.form,
        )
    else:
        if review_assignment.review_form:
            relations = review_models.FormElementsRelationship.objects.filter(
                form=review_assignment.review_form,
            )
        else:
            review_assignment.review_form = submission.review_form
            review_assignment.save()
            relations = review_models.FormElementsRelationship.objects.filter(
                form=submission.review_form,
            )
    if result:
        data_ordered = order_data(decode_json(result.data), relations)
    else:
        data_ordered = None

    template = 'author/submission_review.html'
    context = {
        'author_include': 'shared/view_review.html',
        'submission': submission,
        'review': review_assignment,
        'round_id': round_id,
        'submission_id': submission_id,
        'review_assignment_page': True,
        'data_ordered': data_ordered,
        'result': result,
        'review_rounds': review_rounds,
        'revision_requests': revision_models.Revision.objects.filter(
            book=submission,
            revision_type='review',
        ),
    }

    return render(request, template, context)


@login_required
def tasks(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    template = 'author/submission.html'
    context = {
        'submission': book,
        'tasks': logic.submission_tasks(book, request.user),
        'author_include': 'shared/tasks.html',
    }

    return render(request, template, context)


@login_required
def view_revisions(request, submission_id, revision_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    _revision = get_object_or_404(
        revision_models.Revision,
        pk=revision_id,
        completed__isnull=False,
        book=book,
    )

    review_rounds = models.ReviewRound.objects.filter(
        book=book
    ).order_by(
        '-round_number',
    )

    template = 'author/submission.html'
    context = {
        'revision': _revision,
        'revision_id': _revision.id,
        'submission': book,
        'author_include': 'author/submission_details.html',
        'submission_files': 'author/view_revision.html',
        'update': False,
        'review_rounds': review_rounds,
        'revision_requests':
            revision_models.Revision.objects.filter(
                book=book,
                revision_type='review',
            )
    }

    return render(request, template, context)


@login_required
def revision(request, revision_id, submission_id):
    _revision = get_object_or_404(
        revision_models.Revision,
        pk=revision_id,
        book__owner=request.user,
        completed__isnull=True,
    )
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    form = forms.AuthorRevisionForm(instance=_revision)

    if request.POST:
        form = forms.AuthorRevisionForm(request.POST, instance=_revision)
        if form.is_valid():
            _revision = form.save(commit=False)
            _revision.completed = timezone.now()
            _revision.save()
            _task = models.Task(
                book=_revision.book,
                creator=request.user,
                assignee=_revision.requestor,
                text='Revisions submitted for %s' % _revision.book.title,
                workflow=_revision.revision_type,
            )
            _task.save()
            log.add_log_entry(
                book=book,
                user=request.user,
                kind='revisions',
                message='%s submitted revisions for %s' % (
                    request.user.profile.full_name(),
                    _revision.book.title,
                ),
                short_name='Revisions submitted',
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Revisions recorded, thanks.',
            )
            return redirect(
                reverse(
                    'author_revision_completion_email',
                    kwargs={
                        'submission_id': submission_id,
                        'revision_id': revision_id,
                    }
                )
            )

    has_manuscript = False
    has_additional = False

    for ff in book.files.all():
        if ff.kind == 'manuscript':
            has_manuscript = True
        elif ff.kind == 'additional':
            has_additional = True

    template = 'author/submission.html'
    context = {
        'submission': book,
        'revision': _revision,
        'form': form,
        'has_manuscript': has_manuscript,
        'has_additional': has_additional,
        'author_include': 'author/revision.html',
    }

    return render(request, template, context)


class RevisionCompletionEmail(FormView):
    """
    Allows authors who have just submitted revisions to customise
    a notification email to the requester.
    """
    template_name = 'author/revision_complete_email.html'
    form_class = core_forms.CustomEmailForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(
            models.Book,
            pk=self.kwargs['submission_id']
        )
        self.revision = get_object_or_404(
            revision_models.Revision,
            pk=self.kwargs['revision_id']
        )

        return super(RevisionCompletionEmail, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_form_kwargs(self):
        """Renders the email body and subject for editing using the form
        """
        kwargs = super(RevisionCompletionEmail, self).get_form_kwargs()

        if self.revision.requestor:
            recipient_greeting = email.get_email_greeting(
                recipients=[self.revision.requestor]
            )
        else:
            recipient_greeting = 'Dear sir or madam'

        email_context = {
            'greeting': recipient_greeting,
            'submission': self.submission,
            'sender': self.request.user,
        }

        email_body = email.get_email_content(
            request=self.request,
            setting_name='author_revisions_completed',
            context=email_context,
        )
        email_subject = 'Review completed for {title}: {subtitle}'.format(
            title=self.submission.title,
            subtitle=self.submission.subtitle,
        )

        kwargs['initial'] = {
            'email_subject': email_subject,
            'email_body': email_body,
        }

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RevisionCompletionEmail, self).get_context_data(**kwargs)
        context['submission'] = get_object_or_404(
            models.Book,
            pk=self.kwargs['submission_id']
        )
        return context

    def form_valid(self, form):
        attachments = handle_multiple_email_files(
            request_files=self.request.FILES.getlist('attachments'),
            file_owner=self.request.user,
        )

        other_editors = []
        for book_editor in self.submission.book_editors.all():
            if book_editor != self.revision.requestor:
                other_editors.append(book_editor)

        series_editor = self.submission.get_series_editor()
        if series_editor and series_editor != self.revision.requestor:
            other_editors.append(series_editor)

        copy_email_addresses = []
        if self.revision.requestor:
            recipient_email_addresses = [self.revision.requestor.email]
            copy_email_addresses.extend(
                [editor.email for editor in other_editors]
            )
        else:
            recipient_email_addresses = [
                editor.email for editor in other_editors
            ]

        email.send_prerendered_email(
            from_email=self.request.user.email,
            to=recipient_email_addresses,
            cc=copy_email_addresses,
            subject=form.cleaned_data['email_subject'],
            html_content=form.cleaned_data['email_body'],
            attachments=attachments,
            book=self.submission,
        )

        return super(RevisionCompletionEmail, self).form_valid(form)

    def get_success_url(self):
        return reverse('author_dashboard')


@login_required
def revise_file(request, submission_id, revision_id, file_id):
    _revision = get_object_or_404(
        revision_models.Revision,
        pk=revision_id,
        book__owner=request.user,
    )
    book = _revision.book
    _file = get_object_or_404(models.File, pk=file_id)
    form = forms.AuthorRevisionForm(instance=_revision)

    if request.POST:
        for ff in request.FILES.getlist('update_file'):
            file_label = request.POST.get('file_label', None)
            handle_file_update(
                ff,
                _file,
                book,
                _file.kind,
                request.user,
                label=file_label,
            )
            messages.add_message(request, messages.INFO, 'File updated.')

        return redirect(reverse(
            'author_revision',
            kwargs={
                'submission_id': submission_id,
                'revision_id': _revision.id
            }
        ))

    template = 'author/submission.html'
    context = {
        'submission': book,
        'revision': _revision,
        'file': _file,
        'author_include': 'author/revision.html',
        'submission_files': 'author/revise_file.html',
        'form': form,
    }

    return render(request, template, context)


@login_required
def revision_new_file(request, submission_id, revision_id, file_type):
    _revision = get_object_or_404(
        revision_models.Revision,
        pk=revision_id,
        book__owner=request.user,
    )
    book = _revision.book
    form = forms.AuthorRevisionForm(instance=_revision)

    if request.POST:
        new_upload = request.FILES.get('new_file')
        new_file = handle_file(
            new_upload,
            book,
            'revision',
            request.user,
            label=request.POST.get('file_label')
        )
        new_file.kind = file_type
        new_file.save()
        book.files.add(new_file)

        return redirect(reverse(
            'author_revision',
            kwargs={
                'submission_id': submission_id,
                'revision_id': _revision.id
            }
        ))

    template = 'author/submission.html'
    context = {
        'submission': book,
        'revision': _revision,
        'author_include': 'author/revision.html',
        'submission_files': 'author/revision_new_file.html',
        'form': form,
    }

    return render(request, template, context)


@login_required
def author_production(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    if request.POST and request.GET.get('start', None):
        if request.GET.get('start') == 'typesetting':
            book.stage.typesetting = timezone.now()
            book.stage.save()

    elif request.POST and 'proof_id' in request.POST:
        proof_id = request.POST.get('proof_id')
        author_feedback = request.POST.get('author_feedback')
        proof = get_object_or_404(editor_models.CoverImageProof, pk=proof_id)
        proof.completed = timezone.now()
        proof.note_to_editor = author_feedback
        proof.save()
        log.add_log_entry(
            book=book,
            user=request.user,
            kind='production',
            message='%s %s completed Cover Image Proofs' % (
                request.user.first_name,
                request.user.last_name,
            ),
            short_name='Cover Image Proof Request'
        )
        task.create_new_task(
            book,
            request.user,
            proof.editor,
            "Cover Proofing completed for %s" % book.title,
            workflow='production',
        )
        return redirect(reverse(
            'author_production',
            kwargs={'submission_id': submission_id})
        )

    template = 'author/submission.html'
    context = {
        'author_include': 'author/production/view.html',
        'active': 'production',
        'submission': book,
        'format_list':
            models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book),
    }

    return render(request, template, context)


@login_required
def author_view_typesetter(request, submission_id, typeset_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    typeset = get_object_or_404(models.TypesetAssignment, pk=typeset_id)
    email_text = get_setting('author_typeset_request', 'email')
    author_form = core_forms.TypesetAuthorInvite(instance=typeset)
    if typeset.editor_second_review:
        author_form = core_forms.TypesetTypesetterInvite(instance=typeset)
        email_text = get_setting('typesetter_typeset_request', 'email')

    if request.POST and 'invite_author' in request.POST:
        if not typeset.completed:
            messages.add_message(
                request,
                messages.WARNING,
                (
                    'This typeset has not been completed, '
                    'you cannot invite the author to review.'
                ),
            )
            return redirect(reverse(
                'author_view_typesetter',
                kwargs={
                    'submission_id': submission_id,
                    'typeset_id': typeset_id
                }
            ))
        else:
            typeset.editor_review = timezone.now()
            typeset.save()

    elif request.POST and 'invite_typesetter' in request.POST:
        typeset.editor_second_review = timezone.now()
        typeset.save()
        return redirect(reverse(
            'author_view_typesetter',
            kwargs={
                'submission_id': submission_id,
                'typeset_id': typeset_id
            }
        ))

    elif request.POST and 'send_invite_typesetter' in request.POST:
        author_form = core_forms.TypesetTypesetterInvite(
            request.POST,
            instance=typeset,
        )
        if author_form.is_valid():
            author_form.save()
            typeset.typesetter_invited = timezone.now()
            typeset.save()
            email_text = request.POST.get('email_text')
            core_logic.send_invite_typesetter(
                book,
                typeset,
                email_text,
                request.user,
            )
        return redirect(reverse(
            'author_view_typesetter',
            kwargs={
                'submission_id': submission_id,
                'typeset_id': typeset_id
            }
        ))

    elif request.POST and 'send_invite_author' in request.POST:
        author_form = core_forms.TypesetAuthorInvite(
            request.POST,
            instance=typeset,
        )
        if author_form.is_valid():
            author_form.save()
            typeset.author_invited = timezone.now()
            typeset.save()
            email_text = request.POST.get('email_text')
            core_logic.send_invite_typesetter(
                book,
                typeset,
                email_text,
                request.user,
            )
        return redirect(reverse(
            'author_view_typesetter',
            kwargs={
                'submission_id': submission_id,
                'typeset_id': typeset_id
            }
        ))

    template = 'author/submission.html'
    context = {
        'submission': book,
        'author_include': 'author/production/view.html',
        'submission_files': 'author/production/view_typeset.html',
        'active': 'production',
        'format_list':
            models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book),
        'typeset': typeset,
        'typeset_id': typeset.id,
        'author_form': author_form,
        'email_text': email_text,
    }

    return render(request, template, context)


@login_required
def editing(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)

    template = 'author/submission.html'
    context = {
        'submission': book,
        'author_include': 'author/editing.html',
    }

    return render(request, template, context)


@login_required
def view_copyedit(request, submission_id, copyedit_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    copyedit = get_object_or_404(models.CopyeditAssignment, pk=copyedit_id)
    author_form = core_forms.CopyeditAuthorInvite(instance=copyedit)
    email_text = get_setting('author_copyedit_request', 'email')

    if request.POST and 'invite_author' in request.POST:
        if not copyedit.completed:
            messages.add_message(
                request,
                messages.WARNING,
                (
                    'This copyedit has not been completed, '
                    'you cannot invite the author to review.'
                ),
            )
            return redirect(reverse(
                'view_copyedit',
                kwargs={
                    'submission_id': submission_id, 'copyedit_id': copyedit_id
                }
            ))
        else:
            copyedit.editor_review = timezone.now()
            log.add_log_entry(
                book=book,
                user=request.user,
                kind='editing',
                message='Copyedit Review Completed by %s %s' % (
                    request.user.first_name,
                    request.user.last_name
                ),
                short_name='Editor Copyedit Review Complete'
            )
            copyedit.save()

    elif request.POST and 'send_invite_author' in request.POST:
        attachment = handle_attachment(request, book)
        author_form = core_forms.CopyeditAuthorInvite(
            request.POST,
            instance=copyedit,
        )
        author_form.save()
        copyedit.author_invited = timezone.now()
        copyedit.save()
        email_text = request.POST.get('email_text')
        logic.send_author_invite(
            book,
            copyedit,
            email_text,
            request.user,
            attachment,
        )
        return redirect(reverse(
            'view_copyedit',
            kwargs={
                'submission_id': submission_id,
                'copyedit_id': copyedit_id
            }
        ))

    template = 'author/submission.html'
    context = {
        'submission': book,
        'copyedit': copyedit,
        'author_form': author_form,
        'author_include': 'author/editing.html',
        'submission_files': 'author/view_copyedit.html',
        'email_text': email_text,
        'timeline': core_logic.build_time_line_editing_copyedit(copyedit),
    }

    return render(request, template, context)


@login_required
def view_index(request, submission_id, index_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    index = get_object_or_404(models.IndexAssignment, pk=index_id)

    template = 'author/submission.html'
    context = {
        'submission': book,
        'index': index,
        'author_include': 'author/editing.html',
        'submission_files': 'author/view_index.html',
        'timeline': core_logic.build_time_line_editing_indexer(index),
    }

    return render(request, template, context)


@login_required
def view_chapter(request, submission_id, chapter_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    chapter_formats = models.ChapterFormat.objects.filter(chapter=chapter)

    template = 'author/submission.html'
    context = {
        'submission': book,
        'chapter': chapter,
        'chapter_formats': chapter_formats,
        'author_include': 'author/production/view.html',
        'submission_files': 'author/production/view_chapter.html',
        'active': 'production',
        'format_list':
            models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list':
            models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@login_required
def view_chapter_format(request, submission_id, chapter_id, format_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    chapter_format = get_object_or_404(
        models.ChapterFormat,
        chapter=chapter,
        pk=format_id,
    )

    template = 'author/submission.html'
    context = {
        'submission': book,
        'chapter': chapter,
        'chapter_format': chapter_format,
        'author_include': 'author/production/view.html',
        'submission_files': 'author/production/view_chapter_format.html',
        'active': 'production',
        'format_list':
            models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list':
            models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@login_required
def copyedit_review(request, submission_id, copyedit_id):
    book = get_object_or_404(models.Book, pk=submission_id, owner=request.user)
    copyedit = get_object_or_404(
        models.CopyeditAssignment,
        pk=copyedit_id,
        book__owner=request.user,
        book=book,
        author_invited__isnull=False,
        author_completed__isnull=True,
    )

    form = core_forms.CopyeditAuthor(instance=copyedit)

    if request.POST:
        form = core_forms.CopyeditAuthor(request.POST, instance=copyedit)
        if form.is_valid():
            form.save()
            submission_logic.handle_copyedit_author_labels(
                request.POST,
                copyedit,
                kind='misc',
            )

            copyedit.author_completed = timezone.now()
            copyedit.save()
            log.add_log_entry(
                book=book,
                user=request.user,
                kind='editing',
                message='Copyedit Author review compeleted by %s %s.' % (
                    request.user.first_name,
                    request.user.last_name
                ),
                short_name='Copyedit Author Review Complete',
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Copyedit task complete. Thanks.',
            )
            task.create_new_task(
                book,
                copyedit.book.owner,
                copyedit.requestor,
                "Author Copyediting completed for %s" % book.title,
                workflow='editing',
            )
            return redirect(reverse(
                'editing', kwargs={"submission_id": submission_id, }
            ))

    template = 'author/submission.html'
    context = {
        'submission': book,
        'copyedit': copyedit,
        'author_files': True,
        'author_include': 'author/copyedit.html',
        'submission_files': 'author/copyedit_review.html',
        'form': form,
    }

    return render(request, template, context)


@login_required
def typeset_review(request, submission_id, typeset_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    typeset = get_object_or_404(
        models.TypesetAssignment,
        pk=typeset_id,
        book__owner=request.user,
        book=book,
    )

    form = core_forms.TypesetAuthor(instance=typeset)

    if request.POST:
        form = core_forms.TypesetAuthor(request.POST, instance=typeset)
        if form.is_valid():
            form.save()
            for _file in request.FILES.getlist('typeset_file_upload'):
                new_file = handle_typeset_file(_file, book, typeset, 'typeset')
                typeset.author_files.add(new_file)

            typeset.author_completed = timezone.now()
            typeset.save()
            log.add_log_entry(
                book=book,
                user=request.user,
                kind='production',
                message='Author Typesetting review %s %s completed.' % (
                    request.user.first_name,
                    request.user.last_name
                ),
                short_name='Author Typesetting Review Completed',
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Typesetting task complete. Thanks.',
            )
            task.create_new_task(
                book, typeset.book.owner,
                typeset.requestor,
                "Author Typesetting completed for %s" % book.title,
                workflow='production'
            )
            return redirect(
                reverse('editing', kwargs={"submission_id": submission_id, })
            )

    template = 'author/submission.html'
    context = {
        'submission': book,
        'typeset': typeset,
        'author_include': 'author/typeset.html',
        'submission_files': 'author/typeset_review.html',
        'form': form,
    }

    return render(request, template, context)


@login_required
def author_contract_signoff(request, submission_id, contract_id):
    contract = get_object_or_404(models.Contract, pk=contract_id)
    submission = get_object_or_404(
        models.Book,
        pk=submission_id,
        owner=request.user,
        contract=contract,
    )

    if request.POST:
        author_signoff_form = forms.AuthorContractSignoff(
            request.POST,
            request.FILES,
        )
        if author_signoff_form.is_valid():
            if request.FILES.get('author_file'):
                author_file = request.FILES.get('author_file')
                new_file = handle_file(
                    author_file,
                    submission,
                    'contract',
                    request.user,
                )
                contract.author_file = new_file

            contract.author_signed_off = timezone.now()
            contract.save()
            return redirect(reverse(
                'author_submission',
                kwargs={'submission_id': submission_id}
            ))
    else:
        author_signoff_form = forms.AuthorContractSignoff()

    template = 'author/author_contract_signoff.html'
    context = {
        'submission': 'submission',
        'contract': 'contract',
        'author_signoff_form': 'author_signoff_form',
    }

    return render(request, template, context)


@login_required
def proposal_author_contract_signoff(request, proposal_id, contract_id):
    contract = get_object_or_404(models.Contract, pk=contract_id)
    proposal = get_object_or_404(
        submission_models.Proposal,
        pk=proposal_id,
        owner=request.user,
        contract=contract,
    )

    if request.POST:
        author_signoff_form = forms.AuthorContractSignoff(
            request.POST,
            request.FILES,
        )
        if author_signoff_form.is_valid():
            if request.FILES.get('author_file'):
                author_file = request.FILES.get('author_file')
                new_file = handle_proposal_file(
                    author_file,
                    proposal,
                    'contract',
                    request.user,
                )
                contract.author_file = new_file

            contract.author_signed_off = timezone.now()
            contract.save()
            return redirect(reverse('user_dashboard'))
    else:
        author_signoff_form = forms.AuthorContractSignoff()

    template = 'author/author_contract_signoff.html'
    context = {
        'proposal': 'proposal',
        'contract': 'contract',
        'author_signoff_form': 'proposal_author_signoff_form',
    }

    return render(request, template, context)
