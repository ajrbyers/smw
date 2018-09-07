from __builtin__ import any as string_any
from datetime import datetime
import json
import os
import mimetypes as mime
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from jfu.http import upload_receive, UploadResponse, JFUResponse

from core import (
    email,
    forms as core_forms,
    log,
    logic as core_logic,
    models as core_models,
)
from core.decorators import is_book_editor_or_author
from core.email import get_email_content
from core.files import (
    handle_proposal_file_form,
    handle_multiple_email_files,
)
from core.views import create_proposal_form, serve_proposal_file
from manager import forms as manager_forms
from submission import forms
from submission import logic, models as submission_models
from core.setting_util import get_setting


@login_required
def start_submission(request, book_id=None):
    direct_submissions = get_setting('direct_submissions', 'general')
    default_review_type = get_setting('default_review_type', 'general')
    review_type_selection = get_setting('review_type_selection', 'general')
    ci_required = get_setting('ci_required', 'general')

    checklist_items = submission_models.SubmissionChecklistItem.objects.all()

    if book_id:
        book = get_object_or_404(
            core_models.Book,
            pk=book_id,
            owner=request.user,
        )
        if not book.proposal and not direct_submissions:
            return redirect(reverse('proposal_start'))

        book_form = forms.SubmitBookStageOne(
            instance=book,
            ci_required=ci_required,
        )
        checklist_form = forms.SubmissionChecklist(
            checklist_items=checklist_items,
        )
    else:
        if not direct_submissions:
            return redirect(reverse('proposal_start'))

        book = None
        book_form = forms.SubmitBookStageOne()
        checklist_form = forms.SubmissionChecklist(
            checklist_items=checklist_items,
        )

    if request.method == 'POST':
        if book:
            book_form = forms.SubmitBookStageOne(
                request.POST,
                instance=book,
                ci_required=ci_required,
                review_type_required=review_type_selection,
            )
        else:
            book_form = forms.SubmitBookStageOne(
                request.POST,
                ci_required=ci_required,
                review_type_required=review_type_selection,
            )

        checklist_form = forms.SubmissionChecklist(
            request.POST,
            checklist_items=checklist_items,
        )

        if book_form.is_valid() and checklist_form.is_valid():
            book = book_form.save(commit=False)
            book.owner = request.user

            if not review_type_selection:
                book.review_type = default_review_type

            if not book.submission_stage > 2:
                book.submission_stage = 2
                book.save()
                log.add_log_entry(
                    book,
                    request.user,
                    'submission',
                    'Submission Started',
                    'Submission Started',
                )
            book.save()

            if not book_id and book:
                if book.book_type == 'monograph':
                    logic.copy_author_to_submission(request.user, book)
                elif book.book_type == 'edited_volume':
                    logic.copy_editor_to_submission(request.user, book)

            return redirect(
                reverse('submission_two', kwargs={'book_id': book.id}))

    template = "submission/start_submission.html"
    context = {
        'book_form': book_form,
        'checklist_form': checklist_form,
        'book': book,
        'active': 1,
    }

    return render(request, template, context)


@login_required
def submission_two(request, book_id):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)
    book_form = forms.SubmitBookStageTwo(instance=book)
    logic.check_stage(book, 2)

    if request.method == 'POST':
        book_form = forms.SubmitBookStageTwo(request.POST, instance=book)
        if book_form.is_valid():
            book = book_form.save(commit=False)
            if not book.submission_stage > 3:
                book.submission_stage = 3

            book.save()
            return redirect(
                reverse('submission_three', kwargs={'book_id': book.id}))

    template = "submission/submission_two.html"
    context = {'book': book, 'book_form': book_form, 'active': 2}

    return render(request, template, context)


@login_required
def submission_three(request, book_id):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)
    manuscript_files = core_models.File.objects.filter(
        book=book,
        kind='manuscript',
    )
    additional_files = core_models.File.objects.filter(
        book=book,
        kind='additional',
    )

    logic.check_stage(book, 3)

    if request.method == 'POST':
        if 'next_stage' in request.POST:
            if manuscript_files.count() >= 1:
                if not book.submission_stage > 4:
                    book.submission_stage = 4
                logic.handle_book_labels(request.POST, book, kind='manuscript')
                book.save()

                return redirect(reverse(
                    'submission_three_additional',
                    kwargs={'book_id': book.id})
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'You must upload a Manuscript File.'
                )

        # After any post always redirect to avoid resubmitting of same file.
        return redirect(
            reverse('submission_three', kwargs={'book_id': book.id})
        )

    template = 'submission/submission_three.html'
    context = {
        'book': book,
        'active': 3,
        'manuscript_files': manuscript_files,
        'additional_files': additional_files,
        'manuscript_guidelines': get_setting('manuscript_guidelines', 'general')
    }

    return render(request, template, context)


@login_required
def submission_three_additional(request, book_id):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)
    additional_files = core_models.File.objects.filter(
        book=book,
        kind='additional'
    )

    logic.check_stage(book, 4)

    if request.method == 'POST':
        if not book.submission_stage > 5:
            book.submission_stage = 5
        logic.handle_book_labels(request.POST, book, kind='additional')
        book.save()
        return redirect(reverse('submission_four', kwargs={'book_id': book.id}))

    template = 'submission/submission_three_additional.html'
    context = {
        'book': book,
        'active': 4,
        'additional_files': additional_files,
        'additional_guidelines': get_setting('additional_files_guidelines',
                                             'general')
    }

    return render(request, template, context)


@login_required
def submission_additional_files(request, book_id, file_type):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)

    if file_type == 'additional_files':
        files = core_models.File.objects.filter(book=book, kind='additional')
    elif file_type == 'manuscript_files':
        files = core_models.File.objects.filter(book=book, kind='manuscript')
    else:
        files = None

    if request.POST:
        for _file in files:
            _file.label = request.POST.get('label_%s' % _file.id)
            _file.save()
        return redirect(
            reverse('submission_three', kwargs={'book_id': book.id}))

    template = 'submission/submission_additional_files.html'
    context = {'book': book, 'files': files}

    return render(request, template, context)


@csrf_exempt
def upload(request, book_id, type_to_handle):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)
    _file = upload_receive(request)
    new_file = handle_file(_file, book, type_to_handle, request.user)

    if new_file:
        file_dict = {
            'name': new_file.uuid_filename,
            'size': _file.size,
            'deleteUrl': reverse(
                'jfu_delete',
                kwargs={'book_id': book_id, 'file_pk': new_file.pk}
            ),
            'url': reverse(
                'serve_file',
                kwargs={'submission_id': book_id, 'file_id': new_file.pk}
            ),
            'deleteType': 'POST',
            'ruaId': new_file.pk,
            'original_name': new_file.original_filename,
        }

        return UploadResponse(request, file_dict)
    return HttpResponse('No file')


@csrf_exempt
def upload_delete(request, book_id, file_pk):
    success = True
    try:
        instance = core_models.File.objects.get(pk=file_pk)
        os.unlink(
            '%s/%s/%s' % (settings.BOOK_DIR, book_id, instance.uuid_filename)
        )
        instance.delete()
    except core_models.File.DoesNotExist:
        success = False

    return JFUResponse(request, success)


@login_required
def submission_four(request, book_id):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)
    logic.check_stage(book, 5)

    if request.method == 'POST' and 'next_stage' in request.POST:
        if book.author.count() >= 1 or book.editor.count() >= 1:
            if not book.submission_stage > 6:
                book.submission_stage = 6
                book.save()
            return redirect(
                reverse('submission_five', kwargs={'book_id': book.id}))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'You must add at least one author or editor.'
            )

    template = 'submission/submission_four.html'
    context = {'book': book, 'active': 5}

    return render(request, template, context)


@login_required
def submission_five(request, book_id):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)

    logic.check_stage(book, 6)

    if request.method == 'POST' and 'complete' in request.POST:
        book.submission_date = timezone.now()
        book.slug = slugify(book.title)
        stage = core_models.Stage(
            current_stage='submission',
            submission=book.submission_date,
        )
        stage.save()
        book.stage = stage
        book.save()
        log.add_log_entry(
            book,
            request.user,
            'submission',
            'Submission of %s completed' % book.title,
            'Submission Completed',
        )

        press_editors = core_models.User.objects.filter(  # Send ack email.
            profile__roles__slug='press-editor'
        )
        return redirect(
            reverse(
                'submission_complete_email',
                kwargs={'book_id': book.id}
            )
        )

    template = 'submission/submission_five.html'
    context = {
        'book': book,
        'active': 6,
        'manuscript_files': core_models.File.objects.filter(
            book=book,
            kind='manuscript',
        ),
        'additional_files': core_models.File.objects.filter(
            book=book,
            kind='additional',
        ),
    }

    return render(request, template, context)


class SubmissionCompleteEmail(FormView):
    """Allows authors who have just completed a full book submission
    to customise a notification email before it is sent to the editors.
    """

    template_name = 'shared/editable_notification_email.html'
    form_class = core_forms.CustomEmailForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.book = get_object_or_404(
            core_models.Book,
            pk=self.kwargs['book_id']
        )

        return super(SubmissionCompleteEmail, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_form_kwargs(self):
        """Renders the email body and subject for editing using the form."""
        kwargs = super(SubmissionCompleteEmail, self).get_form_kwargs()

        email_context = {
            'book': self.book,
            'sender': self.request.user,
        }
        email_body = email.get_email_content(
            request=self.request,
            setting_name='completed_submission_notification',
            context=email_context,
        )
        email_subject = (
            u'Submission completed - {title}'.format(
                title=self.book.title,
            )
        )

        kwargs['initial'] = {
            'email_subject': email_subject,
            'email_body': email_body,
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SubmissionCompleteEmail, self).get_context_data(
            **kwargs
        )
        context['heading'] = (
            'Please ensure that you are happy with the below email to the '
            'editor notifying them that you have completed your submission'
        )
        return context

    def form_valid(self, form):
        attachments = handle_multiple_email_files(
            request_files=self.request.FILES.getlist('attachments'),
            file_owner=self.request.user,
        )

        press_editors = User.objects.filter(
            profile__roles__slug='press-editor'
        ).order_by(
            '-first_name'
        )
        email.send_prerendered_email(
            from_email=self.request.user.email,
            to=[
                editor.email for editor in press_editors
                if editor.username != settings.INTERNAL_USER
            ],
            subject=form.cleaned_data['email_subject'],
            html_content=form.cleaned_data['email_body'],
            attachments=attachments,
            book=self.book,
        )

        return super(SubmissionCompleteEmail, self).form_valid(form)

    def get_success_url(self):
        return reverse('author_dashboard')


@login_required
def author(request, book_id, author_id=None):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)

    if author_id:
        if book.author.filter(pk=author_id).exists():
            _author = get_object_or_404(core_models.Author, pk=author_id)
            author_form = forms.AuthorForm(instance=_author)
        else:
            return HttpResponseForbidden()
    else:
        _author = None
        author_form = forms.AuthorForm()

    if request.method == 'POST':
        if _author:
            author_form = forms.AuthorForm(request.POST, instance=_author)
        else:
            author_form = forms.AuthorForm(request.POST)
        if author_form.is_valid():
            _author = author_form.save(commit=False)
            if not _author.sequence:
                _author.sequence = 1
            _author.save()
            if not author_id:
                book.author.add(_author)

            return redirect(
                reverse('submission_four', kwargs={'book_id': book.id}))

    template = "submission/author.html"
    context = {
        'author_form': author_form,
        'book': book,
    }

    return render(request, template, context)


@login_required
def editor(request, book_id, editor_id=None):
    book = get_object_or_404(core_models.Book, pk=book_id, owner=request.user)

    if editor_id:
        if book.editor.filter(pk=editor_id).exists():
            _editor = get_object_or_404(core_models.Editor, pk=editor_id)
            editor_form = forms.EditorForm(instance=_editor)
        else:
            return HttpResponseForbidden()
    else:
        _editor = None
        editor_form = forms.EditorForm()

    if request.method == 'POST':
        if _editor:
            editor_form = forms.EditorForm(request.POST, instance=_editor)
        else:
            editor_form = forms.EditorForm(request.POST)
        if editor_form.is_valid():
            _editor = editor_form.save(commit=False)
            if not _editor.sequence:
                _editor.sequence = 1
            _editor.save()
            if not editor_id:
                book.editor.add(_editor)

            return redirect(
                reverse('submission_four', kwargs={'book_id': book.id}))

    template = "submission/editor.html"
    context = {'author_form': editor_form, 'book': book}

    return render(request, template, context)


@login_required
def delete_incomplete_proposal(request, proposal_id):
    _incomplete_proposal = get_object_or_404(
        submission_models.IncompleteProposal,
        pk=proposal_id,
    )
    _incomplete_proposal.delete()
    messages.add_message(request, messages.SUCCESS, 'Proposal deleted')

    return redirect(reverse('user_dashboard', kwargs={}))


@login_required
def incomplete_proposal(request, proposal_id):
    active_form = core_logic.get_active_proposal_form()
    proposal_form = manager_forms.GeneratedForm(form=active_form)
    _incomplete_journal = get_object_or_404(
        submission_models.IncompleteProposal,
        pk=proposal_id,
    )
    proposal_form_validated = manager_forms.GeneratedForm(form=active_form)

    default_fields_validated = manager_forms.DefaultForm(
        initial={
            'title': _incomplete_journal.title,
            'author': _incomplete_journal.author,
            'subtitle': _incomplete_journal.subtitle},
    )
    default_fields = manager_forms.DefaultForm(
        initial={
            'title': _incomplete_journal.title,
            'author': _incomplete_journal.author,
            'subtitle': _incomplete_journal.subtitle}
    )
    intial_data = {}

    if _incomplete_journal.data:
        data = json.loads(_incomplete_journal.data)

        for k, v in data.items():
            intial_data[k] = v[0]

    proposal_form.initial = intial_data
    proposal_form_validated.initial = intial_data

    if request.method == 'POST' and 'book_submit' in request.POST:
        proposal_form = manager_forms.GeneratedForm(
            request.POST,
            request.FILES,
            form=active_form
        )
        default_fields = manager_forms.DefaultForm(request.POST)

        if proposal_form.is_valid() and default_fields.is_valid():
            defaults = {field.name: field.value() for field in default_fields}
            proposal = submission_models.Proposal(
                form=active_form,
                data=None,
                owner=request.user,
                **defaults
            )
            proposal_type = request.POST.get('proposal-type')

            if proposal_type:
                proposal.book_type = proposal_type

            proposal.save()
            proposal_data_processing(request, proposal, active_form.pk)
            editors = User.objects.filter(profile__roles__slug='press-editor')
            message = (
                "A new  Proposal '%s' with id %s has been submitted by %s ." % (
                    proposal.title,
                    proposal.pk,
                    request.user.username
                )
            )

            for _editor in editors:
                notification = core_models.Task(
                    assignee=_editor,
                    creator=request.user,
                    text=message,
                    workflow='proposal',
                )
                notification.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                'Proposal %s submitted' % proposal.id,
            )
            acknowledgement_email_template = get_setting(
                'proposal_submission_ack',
                'email'
            )

            core_logic.send_proposal_submission_ack(
                request,
                proposal,
                email_text=acknowledgement_email_template,
                owner=request.user,
            )

            log.add_proposal_log_entry(
                proposal=proposal,
                user=request.user,
                kind='proposal',
                message='Proposal has been submitted by %s.' %
                request.user.profile.full_name(),
                short_name='Proposal Submitted',
            )
            _incomplete_journal.delete()

            return redirect(
                reverse(
                    'proposal_submission_email',
                    kwargs={'proposal_id': proposal.id}
                )
            )

        else:
            proposal_form = manager_forms.GeneratedForm(
                request.POST,
                request.FILES,
                form=active_form,
            )
            default_fields = manager_forms.DefaultForm(request.POST)

    elif request.method == 'POST' and 'incomplete' in request.POST:
        proposal_form = manager_forms.GeneratedNotRequiredForm(
            request.POST,
            request.FILES,
            form=active_form
        )
        default_fields = manager_forms.DefaultNotRequiredForm(request.POST)

        if proposal_form.is_valid() and default_fields.is_valid():
            defaults = {field.name: field.value() for field in default_fields}
            _incomplete_journal.form = active_form
            _incomplete_journal.owner = request.user
            _incomplete_journal.title = defaults['title']
            _incomplete_journal.subtitle = defaults['subtitle']
            _incomplete_journal.author = defaults['author']
            proposal_type = request.POST.get('proposal-type')
            _incomplete_journal.book_type = proposal_type
            _incomplete_journal.save()
            proposal_data_processing(
                request,
                _incomplete_journal,
                active_form.pk,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Proposal %s saved' % _incomplete_journal.id
            )
            return redirect(reverse('user_dashboard', kwargs={}))

    template = "submission/start_proposal.html"
    context = {
        'proposal_form': proposal_form,
        'incomplete_proposal': _incomplete_journal,
        'incomplete': True,
        'default_fields': default_fields,
        'proposal_form_validated': proposal_form_validated,
        'default_fields_validated': default_fields_validated,
        'core_proposal': active_form,
    }

    return render(request, template, context)


@login_required
def start_proposal(request):
    submit_proposals = get_setting('submit_proposals', 'general')

    if not submit_proposals:
        return redirect(reverse('user_dashboard'))

    active_form = core_logic.get_active_proposal_form()
    proposal_form = manager_forms.GeneratedForm(form=active_form)
    default_fields = manager_forms.DefaultForm()
    errors = False

    if request.method == 'POST' and 'book_submit' in request.POST:
        proposal_form = manager_forms.GeneratedForm(
            request.POST,
            request.FILES,
            form=active_form
        )
        default_fields = manager_forms.DefaultForm(request.POST)

        if proposal_form.is_valid() and default_fields.is_valid():
            defaults = {field.name: field.value() for field in default_fields}
            proposal = submission_models.Proposal(
                form=active_form,
                data=None,
                owner=request.user,
                **defaults
            )
            proposal_type = request.POST.get('proposal-type')

            if proposal_type:
                proposal.book_type = proposal_type

            proposal.save()
            proposal_data_processing(request, proposal, active_form.pk)
            editors = User.objects.filter(profile__roles__slug='press-editor')
            message = (
                "A new  Proposal '%s' with id %s has been submitted by %s ." % (
                    proposal.title, proposal.pk,
                    request.user.username
                )
            )

            for _editor in editors:
                notification = core_models.Task(
                    assignee=_editor,
                    creator=request.user,
                    text=message,
                    workflow='proposal',
                )
                notification.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                'Proposal %s submitted' % proposal.id,
            )
            email_text = get_setting('proposal_submission_ack', 'email')

            core_logic.send_proposal_submission_ack(
                request,
                proposal,
                email_text=email_text,
                owner=request.user,
            )
            log.add_proposal_log_entry(
                proposal=proposal,
                user=request.user,
                kind='proposal',
                message='Proposal has been submitted by %s.' %
                request.user.profile.full_name(),
                short_name='Proposal Submitted'
            )

            return redirect(
                reverse(
                    'proposal_submission_email',
                    kwargs={'proposal_id': proposal.id}
                )
            )

        else:
            errors = True
            proposal_form = manager_forms.GeneratedForm(
                request.POST,
                request.FILES,
                form=active_form
            )
            default_fields = manager_forms.DefaultForm(request.POST)

    elif request.method == 'POST' and 'incomplete' in request.POST:
        proposal_form = manager_forms.GeneratedNotRequiredForm(
            request.POST,
            request.FILES,
            form=active_form
        )
        default_fields = manager_forms.DefaultNotRequiredForm(request.POST)

        if proposal_form.is_valid() and default_fields.is_valid():
            defaults = {field.name: field.value() for field in default_fields}
            proposal = submission_models.IncompleteProposal(
                form=active_form,
                data=None,
                owner=request.user,
                **defaults
            )
            proposal_type = request.POST.get('proposal-type')

            if proposal_type:
                proposal.book_type = proposal_type

            proposal.save()
            proposal_data_processing(request, proposal, active_form.pk)
            messages.add_message(
                request,
                messages.SUCCESS,
                'Proposal %s saved' % proposal.id,
            )

            return redirect(reverse('user_dashboard', kwargs={}))

    template = "submission/start_proposal.html"
    context = {
        'proposal_form': proposal_form,
        'errors': errors,
        'default_fields': default_fields,
        'core_proposal': active_form,
    }

    return render(request, template, context)


class ProposalSubmissionEmail(FormView):
    """Allows authors who have just submitted a book proposal
    to customise a notification email before it is sent to the editors.
    """

    template_name = 'shared/editable_notification_email.html'
    form_class = core_forms.CustomEmailForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(
            submission_models.Proposal,
            pk=self.kwargs['proposal_id']
        )
        return super(ProposalSubmissionEmail, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_form_kwargs(self):
        """Renders the email body and subject for editing using the form."""
        kwargs = super(ProposalSubmissionEmail, self).get_form_kwargs()

        email_context = {
            'proposal': self.proposal,
            'sender': self.request.user,
        }
        kwargs['initial'] = {
            'email_subject': u'Proposal submitted - {proposal_title}'.format(
                proposal_title=self.proposal.title
            ),
            'email_body': email.get_email_content(
                request=self.request,
                setting_name='new_proposal_notification',
                context=email_context,
            ),
        }

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProposalSubmissionEmail, self).get_context_data(
            **kwargs
        )
        context['heading'] = (
            'Please ensure that you are happy with the below email to the '
            'editor notifying them that you have submitted your proposal'
        )
        return context

    def form_valid(self, form):
        attachments = handle_multiple_email_files(
            request_files=self.request.FILES.getlist('attachments'),
            file_owner=self.request.user,
        )

        press_editors = User.objects.filter(
            profile__roles__slug='press-editor'
        ).order_by(
            '-first_name'
        )
        email.send_prerendered_email(
            from_email=self.request.user.email,
            to=[
                editor.email for editor in press_editors
                if editor.username != settings.INTERNAL_USER
            ],
            subject=form.cleaned_data['email_subject'],
            html_content=form.cleaned_data['email_body'],
            attachments=attachments,
            proposal=self.proposal,
        )

        return super(ProposalSubmissionEmail, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_dashboard')


def proposal_data_processing(request, proposal, proposal_form_id):
    save_dict = {}
    file_fields = core_models.ProposalFormElementsRelationship.objects.filter(
        form=core_models.ProposalForm.objects.get(pk=proposal_form_id),
        element__field_type='upload'
    )
    data_fields = core_models.ProposalFormElementsRelationship.objects.filter(
        ~Q(element__field_type='upload'),
        form=core_models.ProposalForm.objects.get(pk=proposal_form_id)
    )

    for field in file_fields:
        field_name = core_logic.ascii_encode(field.element.name)
        if field_name in request.FILES:
            save_dict[field_name] = [
                handle_proposal_file_form(
                    request.FILES[field_name],
                    proposal,
                    'other',
                    request.user,
                    "Attachment: Uploaded by %s" % request.user.username
                )
            ]

    for field in data_fields:
        # Ensure ASCII field names.
        field_name = core_logic.ascii_encode(field.element.name)
        if field_name in request.POST:
            save_dict[field_name] = [
                request.POST.get(field_name), 'text']

    json_data = smart_text(json.dumps(save_dict))
    proposal.data = json_data
    proposal.save()

    return proposal


@login_required
def proposal_revisions(request, proposal_id):

    active_form = core_logic.get_active_proposal_form()
    proposal = get_object_or_404(
        submission_models.Proposal,
        pk=proposal_id,
        owner=request.user,
        status='revisions_required'
    )
    notes = submission_models.ProposalNote.objects.filter(proposal=proposal)

    overdue = False
    if proposal.revision_due_date.date() < datetime.today().date():
        overdue = True

    proposal_form = manager_forms.GeneratedForm(
        form=core_models.ProposalForm.objects.get(pk=proposal.form.id)
    )
    default_fields = manager_forms.DefaultForm(
        initial={
            'title': proposal.title,
            'author': proposal.author,
            'subtitle': proposal.subtitle
        }
    )
    data = {}
    intial_data = {}

    if proposal.data:
        data = json.loads(proposal.data)
        for k, v in data.items():
            intial_data[k] = v[0]

    proposal_form.initial = intial_data

    if request.POST:
        proposal_form = manager_forms.GeneratedForm(
            request.POST,
            request.FILES,
            form=core_models.ProposalForm.objects.get(pk=proposal.form.id),
        )
        default_fields = manager_forms.DefaultForm(request.POST)

        if proposal_form.is_valid() and default_fields.is_valid():
            messages.add_message(
                request,
                messages.SUCCESS,
                'Revisions for Proposal %s submitted' % proposal.id
            )

            proposal_data_processing(request, proposal, active_form.pk)
            proposal = submission_models.Proposal.objects.get(
                form=core_models.ProposalForm.objects.get(pk=proposal.form.id),
                owner=request.user,
                pk=proposal_id,
            )
            history_proposal = submission_models.HistoryProposal.objects.create(
                proposal=proposal,
                title=proposal.title,
                author=proposal.author,
                subtitle=proposal.subtitle,
                date_submitted=proposal.date_submitted,
                form=proposal.form,
                data=proposal.data,
                date_review_started=proposal.date_review_started,
                review_form=proposal.review_form,
                requestor=proposal.requestor,
                revision_due_date=proposal.revision_due_date,
                date_accepted=proposal.date_accepted,
                book_type=proposal.book_type,
                status=proposal.status,
                owner=proposal.owner,
                user_edited=request.user,
                date_edited=timezone.now(),
                version=proposal.current_version
            )
            history_proposal.save()

            proposal.status = "revisions_submitted"
            defaults = default_fields.cleaned_data
            proposal.title = defaults.get("title")
            proposal.author = defaults.get("author")
            proposal.subtitle = defaults.get("subtitle")
            proposal_type = request.POST.get('proposal-type')
            proposal.current_version = proposal.current_version + 1

            if proposal_type:
                proposal.book_type = proposal_type

            proposal.save()
            notification = core_models.Task(
                assignee=proposal.requestor,
                creator=request.user,
                text="Revisions for Proposal '%s' with id %s submitted" % (
                    proposal.title, proposal.id
                ),
                workflow='proposal',
            )
            notification.save()

            log.add_proposal_log_entry(
                proposal=proposal,
                user=request.user,
                kind='proposal',
                message=(
                    'Revisions for Proposal "%s %s" with id %s '
                    'have been submitted.' % (
                        proposal.title, proposal.subtitle,
                        proposal.pk
                    )
                ),
                short_name='Proposal Revisions Submitted'
            )

            notification.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Proposal %s submitted' % proposal.id
            )
            return redirect(
                reverse('proposal_revisions_submitted', args=[proposal_id])
            )

    template = "submission/proposal_revisions.html"
    context = {
        'proposal_form': proposal_form,
        'proposal': proposal,
        'default_fields': default_fields,
        'data': data,
        'revise': True,
        'notes': notes,
        'overdue': overdue,
        'core_proposal': active_form,
    }

    return render(request, template, context)


class ProposalRevisionCompleteEmail(FormView):
    """Allows authors who have just submitted a revised book proposal
    to customise a notification email before it is sent to the editors.
    """

    template_name = 'shared/editable_notification_email.html'
    form_class = core_forms.CustomEmailForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(
            submission_models.Proposal,
            pk=self.kwargs['proposal_id']
        )
        return super(ProposalRevisionCompleteEmail, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(ProposalRevisionCompleteEmail, self).get_context_data(
            **kwargs
        )
        context['heading'] = (
            'Please ensure that you are happy with the below email to the '
            'editor notifying them that you have completed your review'
        )
        return context

    def get_form_kwargs(self):
        """Renders the email body and subject for editing using the form."""
        kwargs = super(ProposalRevisionCompleteEmail, self).get_form_kwargs()

        email_context = {
            'greeting': u'Dear {editors_name}'.format(
                editors_name=self.proposal.owner.profile.full_name()
            ),
            'proposal': self.proposal,
            'sender': self.request.user,
        }
        kwargs['initial'] = {
            'email_subject': u'Proposal submitted - {proposal_title}'.format(
                proposal_title=self.proposal.title
            ),
            'email_body': email.get_email_content(
                request=self.request,
                setting_name='revised_proposal_notification',
                context=email_context,
            ),
        }
        return kwargs

    def form_valid(self, form):
        attachments = handle_multiple_email_files(
            request_files=self.request.FILES.getlist('attachments'),
            file_owner=self.request.user,
        )
        other_editor_emails = [
            _editor.email for _editor in self.proposal.book_editors.exclude(
                email=self.proposal.owner.email
            )
        ]
        email.send_prerendered_email(
            from_email=self.request.user.email,
            to=self.proposal.owner.email,
            cc=other_editor_emails,
            subject=form.cleaned_data['email_subject'],
            html_content=form.cleaned_data['email_body'],
            attachments=attachments,
            proposal=self.proposal,
        )
        return super(ProposalRevisionCompleteEmail, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_dashboard')


@login_required
def proposal_notes(request, proposal_id, note_id=None):
    proposal = submission_models.Proposal.objects.get(pk=proposal_id)
    notes = submission_models.ProposalNote.objects.filter(proposal=proposal)
    updated = False
    editable = False

    if note_id:
        note = get_object_or_404(submission_models.ProposalNote,
                                 proposal=proposal, pk=note_id)
        if note.user == request.user:
            editable = True
        if not note.date_submitted == note.date_last_updated:
            updated = True
    else:
        note = None
        editable = False

    template = 'submission/view_note.html'
    context = {
        'proposal': proposal,
        'notes': notes,
        'note_id': note_id,
        'current_note': note,
        'editable': editable,
        'updated': updated,
    }

    return render(request, template, context)


@login_required
def proposal_add_note(request, proposal_id):
    proposal = submission_models.Proposal.objects.get(pk=proposal_id)
    if not request.user.profile.is_editor():
        return redirect(reverse(
            'proposal_view_submitted',
            kwargs={'proposal_id': proposal_id})
        )
    notes = submission_models.ProposalNote.objects.filter(proposal=proposal)
    note_form = forms.NoteForm()

    if request.POST:
        note_form = forms.NoteForm(request.POST)
        if note_form.is_valid():
            note_form = note_form.save(commit=False)
            note_form.text = request.POST.get("text")
            note_form.user = request.user
            note_form.proposal = proposal
            note_form.date_submitted = timezone.now()
            note_form.date_last_updated = timezone.now()
            note_form.save()
            return redirect(reverse(
                'proposal_view_submitted',
                kwargs={'proposal_id': proposal.id})
            )

    template = 'submission/new_note.html'
    context = {'proposal': proposal, 'notes': notes, 'note_form': note_form}

    return render(request, template, context)


@login_required
def proposal_update_note(request, proposal_id, note_id):
    proposal = submission_models.Proposal.objects.get(pk=proposal_id)
    notes = submission_models.ProposalNote.objects.filter(proposal=proposal)
    note = get_object_or_404(
        submission_models.ProposalNote,
        proposal=proposal,
        pk=note_id,
    )
    note_form = forms.NoteForm(instance=note)

    if request.POST:
        note_form = forms.NoteForm(request.POST, instance=note)
        if note_form.is_valid():
            note_form.save(commit=False)
            note.text = request.POST.get("text")
            note.user = request.user
            note.date_last_updated = timezone.now()
            note.save()
            return redirect(reverse(
                'proposal_view_submitted', kwargs={'proposal_id': proposal.id})
            )

    template = 'submission/new_note.html'
    context = {
        'proposal': proposal,
        'notes': notes,
        'note_form': note_form,
        'current_note': note,
        'update': True,
    }

    return render(request, template, context)


@login_required
def proposal_view(request, proposal_id):
    proposal = submission_models.Proposal.objects.get(pk=proposal_id)
    active_form = core_logic.get_active_proposal_form()
    notes = submission_models.ProposalNote.objects.filter(proposal=proposal)

    if proposal.owner == request.user:
        viewable = True

    proposal_form = manager_forms.GeneratedForm(
        form=core_models.ProposalForm.objects.get(pk=proposal.form.id)
    )
    default_fields = manager_forms.DefaultForm(
        initial={
            'title': proposal.title,
            'author': proposal.author,
            'subtitle': proposal.subtitle}
    )

    intial_data = {}
    data = {}

    if proposal.data:
        data = json.loads(proposal.data)
        for k, v in data.items():
            intial_data[k] = v[0]

    proposal_form.initial = intial_data
    roles = request.user.profile.roles.all()
    user_roles = [role.slug for role in request.user.profile.roles.all()]

    if string_any('Editor' in role.name for role in roles):
        viewable = True
        _editor = True
        if (
                proposal.requestor and
                not proposal.requestor == request.user and
                'press-editor' not in user_roles
        ):
            _editor = False
    else:
        _editor = False

    if request.POST and _editor:
        proposal_form = manager_forms.GeneratedForm(
            request.POST,
            request.FILES,
            form=core_models.ProposalForm.objects.get(pk=proposal.form.id)
        )
        default_fields = manager_forms.DefaultForm(request.POST)

        if proposal_form.is_valid() and default_fields.is_valid():
            proposal_data_processing(request, proposal, active_form.pk)
            proposal = submission_models.Proposal.objects.get(
                form=core_models.ProposalForm.objects.get(pk=proposal.form.id),
                pk=proposal_id,
            )
            history_proposal = submission_models.HistoryProposal.objects.create(
                proposal=proposal,
                title=proposal.title,
                author=proposal.author,
                subtitle=proposal.subtitle,
                date_submitted=proposal.date_submitted,
                form=proposal.form,
                data=proposal.data,
                date_review_started=proposal.date_review_started,
                review_form=proposal.review_form,
                requestor=proposal.requestor,
                revision_due_date=proposal.revision_due_date,
                date_accepted=proposal.date_accepted,
                book_type=proposal.book_type,
                status=proposal.status,
                owner=proposal.owner,
                user_edited=request.user,
                date_edited=timezone.now(),
                version=proposal.current_version
            )
            history_proposal.save()
            proposal.status = "submission"
            defaults = default_fields.cleaned_data
            proposal.title = defaults.get("title")
            proposal.author = defaults.get("author")
            proposal.subtitle = defaults.get("subtitle")
            proposal_type = request.POST.get('proposal-type')
            proposal.current_version = proposal.current_version + 1

            if proposal_type:
                proposal.book_type = proposal_type

            proposal.requestor = request.user
            proposal.save()

            update_email_text = get_setting('proposal_update_ack', 'email')
            log.add_proposal_log_entry(
                proposal=proposal,
                user=request.user,
                kind='proposal',
                message='Proposal "%s %s" has been updated.' % (
                    proposal.title,
                    proposal.subtitle
                ),
                short_name='Proposal Updated',
            )
            core_logic.send_proposal_update(
                request,
                proposal,
                email_text=update_email_text,
                sender=request.user,
                receiver=proposal.owner,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Proposal %s updated' % proposal.id,
            )
            return redirect(reverse('user_dashboard'))

    if proposal.status == 'accepted' or proposal.status == 'declined':
        not_readonly = False
    else:
        not_readonly = True

    template = "submission/view_proposal.html"
    context = {
        'proposal_form': proposal_form,
        'default_fields': default_fields,
        'proposal': proposal,
        'not_readonly': not_readonly,
        'data': data,
        'revise': True,
        'editor': _editor,
        'viewable': viewable,
        'notes': notes,
        'core_proposal': active_form,
    }

    return render(request, template, context)


@login_required
def proposal_history_view(request, proposal_id, history_id):
    parent_proposal = submission_models.Proposal.objects.get(pk=proposal_id)
    active_form = core_logic.get_active_proposal_form()
    proposal = get_object_or_404(
        submission_models.HistoryProposal,
        proposal=parent_proposal,
        pk=history_id,
    )

    relationships = core_models.ProposalFormElementsRelationship.objects.filter(
        form=proposal.form
    )

    if proposal.data:
        data = json.loads(proposal.data)
    else:
        data = {}

    if not request.POST and request.GET.get('download') == 'docx':
        path = create_proposal_form(proposal)
        return serve_proposal_file(request, path)

    template = "submission/history_view_proposal.html"
    context = {
        'proposal': proposal,
        'relationships': relationships,
        'data': data,
        'core_proposal': active_form,
    }

    return render(request, template, context)


@login_required
def proposal_history(request, proposal_id):
    proposal = submission_models.Proposal.objects.get(pk=proposal_id)
    history = submission_models.HistoryProposal.objects.filter(
        proposal=proposal
    ).order_by(
        'pk'
    )
    active_form = core_logic.get_active_proposal_form()

    if proposal.owner == request.user:
        viewable = True

    proposal_form = manager_forms.GeneratedForm(
        form=core_models.ProposalForm.objects.get(pk=proposal.form.id)
    )
    default_fields = manager_forms.DefaultForm(
        initial={
            'title': proposal.title,
            'author': proposal.author,
            'subtitle': proposal.subtitle
        }
    )
    intial_data = {}
    data = {}

    if proposal.data:
        data = json.loads(proposal.data)
        for k, v in data.items():
            intial_data[k] = v[0]

    proposal_form.initial = intial_data
    roles = request.user.profile.roles.all()
    user_roles = [role.slug for role in request.user.profile.roles.all()]

    if string_any('Editor' in role.name for role in roles):
        viewable = True
        _editor = True
        if (
                proposal.requestor and
                not proposal.requestor == request.user and
                'press-editor' not in user_roles
        ):
            _editor = False
    else:
        _editor = False

    if proposal.status == 'accepted' or proposal.status == 'declined':
        not_readonly = False
    else:
        not_readonly = True

    template = "submission/history_proposal.html"
    context = {
        'proposal_form': proposal_form,
        'default_fields': default_fields,
        'proposal': proposal,
        'not_readonly': not_readonly,
        'data': data,
        'history': history,
        'revise': True,
        'open': True,
        'editor': _editor,
        'viewable': viewable,
        'core_proposal': active_form,
    }

    return render(request, template, context)


def handle_file(file, book, kind, user):
    if file:
        original_filename = smart_text(
            file._get_name()
        ).replace(
            ',', '_'
        ).replace(
            ';', '_'
        )
        filename = str(uuid4()) + str(os.path.splitext(file._get_name())[1])
        folder_structure = os.path.join(
            settings.BASE_DIR,
            'files',
            'books',
            str(book.id)
        )

        if not os.path.exists(folder_structure):
            os.makedirs(folder_structure)

        path = os.path.join(folder_structure, str(filename))
        fd = open(path, 'wb')

        for chunk in file.chunks():
            fd.write(chunk)

        fd.close()
        file_mime = mime.guess_type(filename)

        try:
            file_mime = file_mime[0]
        except IndexError:
            file_mime = 'unknown'

        if not file_mime:
            file_mime = 'unknown'

        new_file = core_models.File(
            mime_type=file_mime,
            original_filename=original_filename,
            uuid_filename=filename,
            stage_uploaded=1,
            kind=kind,
            owner=user,
        )
        new_file.save()
        book.files.add(new_file)
        book.save()

        return new_file


@csrf_exempt
@is_book_editor_or_author
def file_order(request, book_id, type_to_handle):
    book = get_object_or_404(core_models.Book, pk=book_id)

    if type_to_handle == 'manuscript':
        id_to_get = 'man'
        files = core_models.File.objects.filter(book=book, kind='manuscript')
    elif type_to_handle == 'additional':
        id_to_get = 'add'
        files = core_models.File.objects.filter(book=book, kind='additional')
    elif type_to_handle == 'author':
        id_to_get = 'auth'
        files = core_models.Author.objects.filter(book=book)
    elif type_to_handle == 'editor':
        id_to_get = 'edit'
        files = core_models.Editor.objects.filter(book=book)

    if request.POST:
        ids = request.POST.getlist('%s[]' % id_to_get)
        ids = [int(_id) for _id in ids]
        for file in files:
            file.sequence = ids.index(file.id)  # Get the index.
            file.save()

    return HttpResponse('Thanks')
