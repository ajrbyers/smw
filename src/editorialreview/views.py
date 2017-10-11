import os
import json
import mimetypes

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core import setting_util, email, models as core_models, logic as core_logic
from core.decorators import is_reviewer, is_editor, is_book_editor
from core.email import send_email
from core.files import handle_attachment, handle_email_file
from editor import logic as editor_logic
from editorialreview import logic, forms, models
from manager import models as manager_models
from review import models as review_models, forms as review_forms
from submission import models as submission_models



@is_editor
def add_editorial_review(request, submission_type, submission_id):
    """ Create a new editorial review. """
    check = None
    submission = logic.get_submission(submission_type, submission_id)
    editorial_reviewers = manager_models.GroupMembership.objects.filter(group__group_type='editorial_group')
    editorial_groups = manager_models.Group.objects.filter(group_type='editorial_group')
    form = forms.EditorialReviewForm()

    if request.POST:
        form = forms.EditorialReviewForm(request.POST)
        reviewer = User.objects.get(pk=request.POST.get('reviewer'))
        review_form = review_models.Form.objects.get(ref=request.POST.get('review_form'))

        check = logic.check_editorial_post(form, reviewer, review_form)

        if check.get('status'):
            review = logic.handle_editorial_post(
                request,
                submission,
                form,
                reviewer,
                review_form
            )
            return redirect(
                reverse(
                    'email_editorial_review',
                    kwargs={
                        'review_id': review.id
                    }
                )
            )

    template = 'editorialreview/add_editorial_review.html'
    context = {
        'submission': submission,
        'submission_type': submission_type,
        'editorial_reviewers': editorial_reviewers,
        'editorial_groups': editorial_groups,
        'form': form,
        'review_forms': review_models.Form.objects.all(),
        'check': check,
    }

    return render(request, template, context)


@is_editor
def remove_editorial_review(request, submission_id, review_id):
    """Remove an editorial review.
    Currently just handles full submissions but can be expanded.
    """
    review_assignment = get_object_or_404(models.EditorialReview, pk=review_id)
    review_assignment.delete()
    messages.add_message(
        request,
        messages.INFO,
        'Editorial review assignment {} deleted'.format(review_id)
    )

    return redirect(
        reverse(
            'editor_review',
            kwargs={
                'submission_id': submission_id
            }
        )
    )


@is_editor
def withdraw_editorial_review(request, submission_id, review_id):
    """Withdraw an editorial review.
    Currently just handles full submissions but can be expanded.
    """
    review_assignment = get_object_or_404(models.EditorialReview, pk=review_id)
    if review_assignment.withdrawn:
        review_assignment.withdrawn = False
    else:
        review_assignment.withdrawn = True

    review_assignment.save()
    messages.add_message(
        request,
        messages.INFO,
        'Editorial review assignment {} {}'.format(
            review_id,
            'withdrawn' if review_assignment.withdrawn else 're-enabled'
        )
    )

    return redirect(
        reverse(
            'editor_view_editorial_review',
            kwargs={
                'submission_id': submission_id,
                'editorial_review_id': review_id
            }
        )
    )

@is_editor
def update_editorial_review_due_date(request, submission_id, review_id):
    """ Update the due date of an editorial review. """
    submission = get_object_or_404(core_models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.EditorialReview, pk=review_id)
    previous_due_date = review_assignment.due

    if request.POST:
        email_text = core_models.Setting.objects.get(group__name='email', name='review_due_ack').value
        due_date = request.POST.get('due_date', None)
        notify = request.POST.get('email', None)

        if due_date:
            if not str(due_date) == str(previous_due_date):
                review_assignment.due = due_date
                review_assignment.save()

                if notify:
                    editor_logic.send_review_update(
                        submission,
                        review_assignment,
                        email_text,
                        request.user,
                        attachment=None
                    )
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Due date updated.'
                )

            return redirect(
                reverse(
                    'editor_view_editorial_review',
                    kwargs={
                        'submission_id': submission_id,
                        'editorial_review_id': review_id
                    }
                )
            )

    template = 'editorialreview/update_editorial_review_due_date.html'
    context = {
        'submission': submission,
        'review': review_assignment,
    }

    return render(request, template, context)


@is_editor
def add_editorial_review_files(request, submission_type, submission_id):
    """Add files to editorial review.
    Currently set up for full submissions only, and only linked in
    if creating editorial review for full submissions, but
    could be extended to include proposals by passing it 
    to submission_type and adding logic below.
    """

    submission = get_object_or_404(core_models.Book, pk=submission_id)

    if request.POST:
        files = core_models.File.objects.filter(pk__in=request.POST.getlist('file'))
        for file in files:
            submission.editorial_review_files.add(file)

        messages.add_message(request, messages.SUCCESS, '%s files added to Review' % files.count())

        return redirect(
            reverse(
                'add_editorial_review',
                kwargs={
                    'submission_type': submission_type,
                    'submission_id': submission_id
                }
            )
        )

    template = 'editorialreview/add_editorial_review_files.html'
    context = {
        'submission': submission,
    }

    return render(request, template, context)

@is_editor
def remove_editorial_review_file(request, submission_type, submission_id, file_id):
    """ Remove a file from a submission's editorial review files list """
    submission = get_object_or_404(core_models.Book, pk=submission_id)
    file = get_object_or_404(submission.editorial_review_files, pk=file_id)

    submission.editorial_review_files.remove(file)

    return redirect(
        reverse(
            'add_editorial_review',
            kwargs={
                'submission_type': submission_type,
                'submission_id': submission_id
            }
        )
    )


@is_editor
def email_editorial_review(request, review_id):
    """Preview the content of an editorial review request email
     then send it with any necessary attachments.
     """

    review = get_object_or_404(models.EditorialReview, pk=review_id)
    email_setting = 'editorial_review_{0}'.format(review.content_type)
    task_url = logic.get_task_url(review, request)

    email_text = email.get_email_content(
        request,
        email_setting,
        {
            'review': review,
            'sender': request.user,
            'task_url': task_url
        }
    )
    subject = setting_util.get_setting(
        setting_name='editorial_review',
        setting_group_name='email_subject',
        default='Editorial Review Request'
    )

    if request.POST:
        email_text = request.POST.get('email_text')
        attachment_files = request.FILES.getlist('attachment')
        attachments = []

        if attachment_files:
            for file in attachment_files:
                attachment = handle_email_file(
                    file,
                    'other',
                    request.user,
                    "Attachment: Uploaded by %s" % (request.user.username)
                )
                attachments.append(attachment)

        if review.content_type.model == 'proposal':
            email.send_prerendered_email(
                request,
                email_text,
                subject,
                review.user.email,
                attachments=attachments,
                book=None,
                proposal=review.content_object
            )
            return redirect(
                reverse(
                    'view_proposal',
                    kwargs={
                        'proposal_id': review.content_object.id
                    }
                )
            )
        else:
            email.send_prerendered_email(
                request,
                email_text,
                subject,
                review.user.email,
                attachments=attachments,
                book=review.content_object,
                proposal=None
            )
            return redirect(
                reverse(
                    'editor_review',
                    kwargs={
                        'submission_id': review.content_object.id
                    }
                )
            )

    template = 'editorialreview/email_editorial_review.html'
    context = {
        'review': review,
        'email_text': email_text,
        'subject': subject,
    }

    return render(request, template, context)


@is_editor
def view_editorial_review(request, review_id):
    """ View a completed editorial review """

    review = get_object_or_404(models.EditorialReview, pk=review_id)

    result = review.results
    relations = review_models.FormElementsRelationship.objects.filter(form=result.form)
    data_ordered = core_logic.order_data(core_logic.decode_json(result.data), relations)

    template = 'editorialreview/view_editorial_review.html'
    context = {
        'review': review,
        'relations': relations,
        'data_ordered': data_ordered,
        'result': result,
    }

    return render(request, template, context)


def editorial_review(request, review_id):
    """ Complete an editorial review."""

    access_key = request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            access_key=access_key,
            completed__isnull=True
        )
    else:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            user=request.user,
            completed__isnull=True
        )

    form = review_forms.GeneratedForm(form=review.review_form)
    recommendation_form = forms.RecommendationForm(instance=review)

    if review.content_type.model == 'book':
        peer_reviews = core_models.ReviewAssignment.objects.filter(
            book=review.content_object,
            completed__isnull=False
        )
    else:
        peer_reviews = submission_models.ProposalReview.objects.filter(
            proposal=review.content_object,
            completed__isnull=False
        )

    completed_editorial_reviews = models.EditorialReview.objects.filter(
        object_id=review.content_object.id,
        content_type=review.content_type,
        completed__isnull=False
    )

    if request.POST:
        form = review_forms.GeneratedForm(
            request.POST,
            request.FILES,
            form=review.review_form
        )
        recommendation_form = forms.RecommendationForm(
            request.POST,
            instance=review
        )

        if form.is_valid() and recommendation_form.is_valid():
            logic.handle_generated_form_post(review, request)
            review.completed = timezone.now()
            review.save()

            return redirect(
                reverse(
                'editorial_review_thanks',
                    kwargs={
                        'review_id': review_id
                    }
                )
            )

    template = 'editorialreview/editorial_review.html'
    context = {
        'review': review,
        'access_key': access_key,
        'form': form,
        'recommendation_form': recommendation_form,
        'peer_reviews': peer_reviews,
        'completed_editorial_reviews': completed_editorial_reviews
    }

    return render(request, template, context)


def view_non_editorial_review(request, review_id, non_editorial_review_id):

    access_key = request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            access_key=access_key,
            completed__isnull=True
        )
    else:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            user=request.user,
            completed__isnull=True
        )

    if review.content_type.model == 'book':
        peer_review = core_models.ReviewAssignment.objects.get(pk=non_editorial_review_id, completed__isnull=False)
    else:
        peer_review = submission_models.ProposalReview.objects.get(pk=non_editorial_review_id, completed__isnull=False)

    result = peer_review.results
    relations = review_models.FormElementsRelationship.objects.filter(form=result.form)
    data_ordered = core_logic.order_data(core_logic.decode_json(result.data), relations)

    template = 'editorialreview/view_non_editorial_review.html'
    context = {
        'review': review,
        'peer_review': peer_review,
        'data_ordered': data_ordered,
        'relations': relations,
        'result': result,
    }

    return render(request, template, context)


def view_content_summary(request, review_id):

    access_key = request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            access_key=access_key,
            completed__isnull=True
        )
    else:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            user=request.user,
            completed__isnull=True
        )

    if review.content_type.model == 'proposal':
        data = json.loads(review.content_object.data)
        relationships = core_models.ProposalFormElementsRelationship.objects.filter(form=review.content_object.form)
        proposal = get_object_or_404(submission_models.Proposal, pk=review.object_id)

        template = 'editorialreview/view_content_summary_proposal.html'
        context = {
            'data': data,
            'relationships': relationships,
            'review': review,
            'proposal': proposal,
        }
    else:
        template = 'editorialreview/view_content_summary_book.html'
        context = {
            'submission': review.content_object,
            'review': review,
        }

    return render(request, template, context)


@is_reviewer
def download_er_file(request, file_id, review_id):

    access_key = request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            access_key=access_key
        )
    else:
        review = get_object_or_404(
            models.EditorialReview,
            pk=review_id,
            user=request.user
        )

    _file = get_object_or_404(core_models.File, pk=file_id)
    file_path = os.path.join(settings.BOOK_DIR, str(review.content_object.id), _file.uuid_filename)

    try:
        fsock = open(file_path, 'r')
        mimetype = mimetypes.guess_type(file_path)
        response = StreamingHttpResponse(fsock, content_type=mimetype)
        response['Content-Disposition'] = "attachment; filename=%s" % (_file.original_filename)
        # log.add_log_entry(
        #     book=book,
        #     user=request.user,
        #     kind='file',
        #     message='File {} downloaded.'.format( _file.original_filename),
        #     short_name='Download'
        # )
        return response

    except IOError:
        messages.add_message(request, messages.ERROR, 'File not found. %s' % (file_path))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@is_editor
def download_editor_er_file(request, file_id, review_id):

    review = get_object_or_404(models.EditorialReview, pk=review_id)
    _file = get_object_or_404(core_models.File, pk=file_id)
    file_path = os.path.join(settings.BOOK_DIR, str(review.content_object.id), _file.uuid_filename)

    try:
        fsock = open(file_path, 'r')
        mimetype = mimetypes.guess_type(file_path)
        response = StreamingHttpResponse(fsock, content_type=mimetype)
        response['Content-Disposition'] = "attachment; filename=%s" % (_file.original_filename)
        # log.add_log_entry(
        #     book=book,
        #     user=request.user,
        #     kind='file',
        #     message='File {} downloaded.'.format( _file.original_filename),
        #     short_name='Download'
        # )
        return response

    except IOError:
        messages.add_message(request, messages.ERROR, 'File not found. %s' % (file_path))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def editorial_review_thanks(request, review_id):
    """ 'Thank you' screen after editorial review is completed. """

    template = 'editorialreview/editorial_review_thanks.html'
    context = {
        'review_id': review_id,
    }

    return render(request, template, context)


def editorial_reviewer_email_editor(request, submission_type, review_id, user_id=None):
    """ Email a book or press editor as an editorial reviewer. """

    editorial_review = get_object_or_404(models.EditorialReview.objects, pk=review_id)
    editors = editorial_review.content_object.book_editors.all()
    if not editors:
        editors = editorial_review.content_object.press_editors.all()

    user = None
    from_value = 'Please enter your email address'
    to_value = ''

    if user_id:
        user = get_object_or_404(User, pk=user_id)
        from_value = "{};".format(user.email)

    if editors:
        to_value = str([editor.email for editor in editors])

    sent = False

    if request.POST:
        attachment_files = request.FILES.getlist('attachment')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        to_addresses = request.POST.get('to_values').split(';')
        cc_addresses = request.POST.get('cc_values').split(';')
        bcc_addresses = request.POST.get('bcc_values').split(';')

        to_list = logic.clean_email_list(to_addresses)
        cc_list = logic.clean_email_list(cc_addresses)
        bcc_list = logic.clean_email_list(bcc_addresses)

        attachments = []  # To create list of attachment objects, rather than InMemoryUploadedFiles.

        if attachment_files:
            for attachment in attachment_files:
                attachment = handle_email_file(
                    attachment,
                    'other',
                    request.user,
                    'Attachment: Uploaded by {}'.format(request.user.username)
                )
                attachments.append(attachment)

        if to_addresses:
            if attachment_files:
                send_email(
                    subject=subject,
                    context={},
                    from_email=request.user.email,
                    to=to_list,
                    bcc=bcc_list,
                    cc=cc_list,
                    html_template=body,
                    attachments=attachments
                )

            else:
                send_email(
                    subject=subject,
                    context={},
                    from_email=request.user.email,
                    to=to_list,
                    bcc=bcc_list,
                    cc=cc_list,
                    html_template=body
                )
            message = 'E-mail with subject {} was sent.'.format(subject)

            return HttpResponse(
                '<script type="text/javascript">window.alert("' + message +
                '")</script><script type="text/javascript">window.close()</script>'
            )

    source = "/email/get/users/"

    template = 'core/email.html'
    context = {
        'from': request.user,
        'to_value': to_value,
        'source': source,
        'user_id': user_id,
        'sent': sent,

    }
    return render(request, template, context)