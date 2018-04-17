import json
import mimetypes as mime
import os
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.encoding import smart_text

from core import models as core_models, logic as core_logic
from review import models as review_models
from submission import models as submission_models


def get_submission(submission_type, submission_id):
    if submission_type == 'proposal':
        return submission_models.Proposal.objects.get(pk=submission_id)
    return core_models.Book.objects.get(pk=submission_id)


def check_editorial_post(form, reviewers, review_form):
    c_form, c_reviewers, c_review_form, status = False, False, False, False

    if form.is_valid():
        c_form = True

    if reviewers:
        c_reviewers = True

    if review_form:
        c_review_form = True

    if c_form and c_reviewers and c_review_form:
        status = True

    response = {
        'status': status,
        'c_form': c_form,
        'c_reviewers': c_reviewers,
        'c_review_form': c_review_form,
    }

    return response


def handle_editorial_post(request, submission, form, reviewer, review_form):
    new_editorial_review = form.save(commit=False)
    new_editorial_review.user = reviewer
    new_editorial_review.access_key = uuid4()
    new_editorial_review.review_form = review_form

    new_editorial_review.content_type = ContentType.objects.get_for_model(
        submission,
    )
    new_editorial_review.object_id = submission.id
    new_editorial_review.save()

    return new_editorial_review


def get_task_url(review, request):
    protocol = 'https://' if request.is_secure() else 'http://'
    task_url = '{0}{1}{2}'.format(
        protocol,
        request.get_host(),
        reverse('editorial_review', kwargs={'review_id': review.id})
    )

    return task_url


def handle_generated_form_post(review_assignment, request):
    save_dict = {}
    file_fields = review_models.FormElementsRelationship.objects.filter(
        form=review_assignment.review_form,
        element__field_type='upload',
    )
    data_fields = review_models.FormElementsRelationship.objects.filter(
        ~Q(element__field_type='upload'),
        form=review_assignment.review_form,
    )

    for field in file_fields:
        field_name = core_logic.ascii_encode(field.element.name)
        if field_name in request.FILES:
            save_dict[field_name] = [
                handle_review_file(
                    request.FILES[field_name],
                    review_assignment,
                    'reviewer'
                )
            ]

    for field in data_fields:
        field_name = core_logic.ascii_encode(field.element.name)
        if field_name in request.POST:
            save_dict[field_name] = [
                request.POST.get(field_name),
                'text'
            ]

    json_data = smart_text(json.dumps(save_dict))
    form_results = review_models.FormResult(
        form=review_assignment.review_form,
        data=json_data,
    )
    form_results.save()
    review_assignment.results = form_results
    review_assignment.save()

    if request.FILES.get('review_file_upload'):
        handle_review_file(
            request.FILES.get('review_file_upload'),
            review_assignment,
            'reviewer',
        )


def handle_review_file(_file, review_assignment, kind, return_file=None):
    original_filename = smart_text(
        _file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    folder = "{0}s".format(review_assignment.content_type)
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        folder,
        str(review_assignment.content_object.id)
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    _path = os.path.join(folder_structure, str(filename))
    fd = open(_path, 'wb')
    [fd.write(chunk) for chunk in _file.chunks()]
    fd.close()
    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
        if not file_mime:
            file_mime = 'unknown'
    except IndexError:
        file_mime = 'unknown'

    new_file = core_models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        owner=review_assignment.user,
    )
    new_file.save()
    review_assignment.files.add(new_file)

    if return_file:
        return new_file

    return _path
