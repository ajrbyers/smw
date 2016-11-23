import os, json, mimetypes

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseRedirect, Http404, HttpResponse, StreamingHttpResponse
from django.conf import settings
from django.contrib import messages

from manager import models as manager_models
from editorialreview import logic, forms, models
from review import models as review_models, forms as review_forms
from core import setting_util, email, models as core_models, logic as core_logic
from core.files import handle_attachment, handle_email_file
from submission import models as submission_models

from core.decorators import is_reviewer, is_editor, is_book_editor

@is_editor
def add_editorial_review(request, submission_type, submission_id):
    check = None
    submission = logic.get_submission(submission_type, submission_id)
    editorial_reviewers = manager_models.GroupMembership.objects.filter(group__group_type='editorial_group')
    form = forms.EditorialReviewForm()

    if request.POST:
        form = forms.EditorialReviewForm(request.POST)
        reviewer = User.objects.get(pk=request.POST.get('reviewer'))
        review_form = review_models.Form.objects.get(ref=request.POST.get('review_form'))

        check = logic.check_editorial_post(form, reviewer, review_form)

        if check.get('status'):
            review = logic.handle_editorial_post(request, submission, form, reviewer, review_form)
            return redirect(reverse('email_editorial_review', kwargs={'review_id': review.id}))


    template = 'editorialreview/add_editorial_review.html'
    context = {
        'submission': submission,
        'submission_type': submission_type,
        'editorial_reviewers': editorial_reviewers,
        'form': form,
        'review_forms': review_models.Form.objects.all(),
        'check': check,
    }

    return render(request, template, context)

@is_editor
def email_editorial_review(request, review_id):

    review = get_object_or_404(models.EditorialReview, pk=review_id)
    email_setting = 'editorial_review_{0}'.format(review.content_type)
    task_url = logic.get_task_url(review, request)
    email_text = email.get_email_content(request, email_setting, {'review': review, 'sender': request.user, 'task_url': task_url})
    subject = setting_util.get_setting(setting_name='editorial_review', setting_group_name='email_subject', default='Editorial Review Request')

    if request.POST:
        email_text = request.POST.get('email_text')
        if request.FILES.get('attachment'):
            attachment = handle_email_file(request.FILES.get('attachment'), 'other', request.user,
                                        "Attachment: Uploaded by %s" % (request.user.username))
        else:
            attachment = None

        if review.content_type.model == 'proposal':
            email.send_prerendered_email(request, email_text, subject, review.user.email, attachments=[attachment], book=None, proposal=review.content_object)
            return redirect(reverse('view_proposal', kwargs={'proposal_id': review.content_object.id}))
        else:
            email.send_prerendered_email(request, email_text, subject, review.user.email, attachments=[attachment], book=review.content_object, proposal=None)
            return redirect(reverse('editor_review', kwargs={'submission_id': review.content_object.id}))

    template = 'editorialreview/email_editorial_review.html'
    context = {
        'review': review,
        'email_text': email_text,
        'subject': subject,
    }

    return render(request, template, context)

@is_editor
def view_editorial_review(request, review_id):

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

    access_key = request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(models.EditorialReview, pk=review_id, access_key=access_key, completed__isnull=True)
    else:
        review = get_object_or_404(models.EditorialReview, pk=review_id, user=request.user, completed__isnull=True)

    form = review_forms.GeneratedForm(form=review.review_form)
    recommendation_form = forms.RecommendationForm(instance=review)

    if review.content_type.model == 'book':
        peer_reviews = core_models.ReviewAssignment.objects.filter(book=review.content_object, completed__isnull=False)
    else:
        peer_reviews = submission_models.ProposalReview.objects.filter(proposal=review.content_object, completed__isnull=False)

    if request.POST:
        form = review_forms.GeneratedForm(request.POST, request.FILES, form=review.review_form)
        recommendation_form = forms.RecommendationForm(request.POST, instance=review)

        if form.is_valid() and recommendation_form.is_valid():
            logic.handle_generated_form_post(review, request)
            review.completed = timezone.now()
            review.save()
            return redirect(reverse('editorial_review_thanks'))

    template = 'editorialreview/editorial_review.html'
    context = {
        'review': review,
        'access_key': access_key,
        'form': form,
        'recommendation_form': recommendation_form,
        'peer_reviews': peer_reviews,
    }

    return render(request, template, context)

def view_non_editorial_review(request, review_id, non_editorial_review_id):

    access_key = request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(models.EditorialReview, pk=review_id, access_key=access_key, completed__isnull=True)
    else:
        review = get_object_or_404(models.EditorialReview, pk=review_id, user=request.user, completed__isnull=True)

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
        review = get_object_or_404(models.EditorialReview, pk=review_id, access_key=access_key, completed__isnull=True)
    else:
        review = get_object_or_404(models.EditorialReview, pk=review_id, user=request.user, completed__isnull=True)

    if review.content_type.model == 'proposal':
        data = json.loads(review.content_object.data)
        relationships = core_models.ProposalFormElementsRelationship.objects.filter(form=review.content_object.form)

        template = 'editorialreview/view_content_summary_proposal.html'
        context = {
            'data': data,
            'relationships': relationships,
            'review': review,
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

    print request.GET.get('access_key')

    if access_key:
        review = get_object_or_404(models.EditorialReview, pk=review_id, access_key=access_key)
    else:
        review = get_object_or_404(models.EditorialReview, pk=review_id, user=request.user)

    _file = get_object_or_404(core_models.File, pk=file_id)

    file_path = os.path.join(settings.BOOK_DIR, str(review.content_object.id), _file.uuid_filename)

    try:
        fsock = open(file_path, 'r')
        mimetype = mimetypes.guess_type(file_path)
        response = StreamingHttpResponse(fsock, content_type=mimetype)
        response['Content-Disposition'] = "attachment; filename=%s" % (_file.original_filename)
        # log.add_log_entry(book=book, user=request.user, kind='file', message='File %s downloaded.' % _file.original_filename, short_name='Download')
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
        # log.add_log_entry(book=book, user=request.user, kind='file', message='File %s downloaded.' % _file.original_filename, short_name='Download')
        return response
    except IOError:
        messages.add_message(request, messages.ERROR, 'File not found. %s' % (file_path))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def editorial_review_thanks(request):

    template = 'editorialreview/editorial_review_thanks.html'
    context = {}

    return render(request, template, context)
