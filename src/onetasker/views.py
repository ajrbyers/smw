from datetime import datetime
import mimetypes as mime
import os
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.csrf import csrf_exempt

from jfu.http import (
    JFUResponse,
    upload_receive,
    UploadResponse,
)

from core import logic as core_logic, models, log
from core.decorators import is_onetasker
from core.email import get_email_body
from core.util import get_setting
from submission.logic import handle_book_labels

from .logic import (
    add_file,
    complete_task,
    get_assignemnt_form,
    get_assignment,
    get_submitted_files,
    get_unposted_form,
    notify_editor,
    right_block,
)


@is_onetasker
def dashboard(request):
    onetasker_tasks = core_logic.onetasker_tasks(request.user)
    template = 'onetasker/dashboard.html'
    context = {
        'completed_tasks': onetasker_tasks.get('completed'),
        'active_tasks': onetasker_tasks.get('active'),
        'completed_count': len(onetasker_tasks.get('completed')),
        'active_count': len(onetasker_tasks.get('active'))

    }

    return render(request, template, context)


def task_hub(request, assignment_type, assignment_id, about=None):

    assignment = get_assignment(assignment_type, assignment_id)
    form = get_unposted_form(request, assignment_type, assignment)
    center_block = (
        'onetasker/elements/submission_details.html' if about
        else 'onetasker/elements/files.html'
    )
    block = right_block(assignment)
    submitted_files = get_submitted_files(assignment)

    if assignment_type == 'copyedit':
        instructions = get_setting('instructions_for_task_copyedit', 'general')
    elif assignment_type == 'typesetting':
        instructions = get_setting('instructions_for_task_typeset', 'general')
    elif assignment_type == 'indexing':
        instructions = get_setting('instructions_for_task_index', 'general')
    else:
        instructions = ""

    if request.POST:
        decision = request.POST.get('decision', None)  # Handle decision.
        if decision == 'accept':
            assignment.accepted = datetime.now()
            assignment.save()
            return redirect(reverse(
                'onetasker_task_hub',
                kwargs={
                    'assignment_type': assignment_type,
                    'assignment_id': assignment_id
                }
            ))
        elif decision == 'decline':
            assignment.declined = datetime.now()
            assignment.save()
            messages.add_message(request, messages.SUCCESS, 'Task declined.')
            return redirect(reverse(
                'onetasker_task_hub_decline',
                kwargs={
                    'assignment_type': assignment_type,
                    'assignment_id': assignment_id
                }
            ))
        elif 'task' in request.POST:  # Handle submission.
            form = get_assignemnt_form(
                request,
                assignment_type,
                assignment,
            )
            if form.is_valid():
                assignment = form.save(commit=False)
                notify_editor(
                    assignment,
                    '%s task completed' % (assignment.type())
                )
                complete_task(assignment)
                handle_book_labels(request.POST, assignment.book, kind='misc')
                assignment.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Task completed. Thanks!'
                )
                return redirect(reverse(
                    'onetasker_task_hub',
                    kwargs={
                        'assignment_type': assignment_type,
                        'assignment_id': assignment_id
                    }
                ))

        elif 'label' in request.POST:  # Handle label.
            _file = get_object_or_404(
                models.File,
                pk=request.POST.get('file_id'),
            )
            _file.label = request.POST.get('label')
            _file.save()

    template = 'onetasker/taskhub.html'
    context = {
        'submission': assignment.book,
        'assignment': assignment,
        'form': form,
        'center_block': center_block,
        'right_block': block,
        'files': submitted_files,
        'about': about,
        'editors': core_logic.get_editors(assignment.book),
        'instructions': instructions,
    }

    return render(request, template, context)


@is_onetasker
def task_hub_decline(request, assignment_type, assignment_id,):

    assignment = get_assignment(assignment_type, assignment_id)
    email_text = get_email_body(
        request=request,
        setting_name='task_decline',
        context={'sender': request.user, 'receiver': assignment.requestor}
    )

    if request.POST:
        if assignment_type == 'copyedit':
            format_kind = "copyedit"
            assignment_user = assignment.copyeditor
        elif assignment_type == 'typesetting':
            format_kind = "typeset"
            assignment_user = assignment.typesetter
        elif assignment_type == 'indexing':
            format_kind = "index"
            assignment_user = assignment.indexer

        log.add_log_entry(
            book=assignment.book,
            user=request.user,
            kind=format_kind,
            message='%s assignment declined by %s.' % (
                assignment_type.title(),
                assignment_user.profile.full_name()
            ),
            short_name='Assignment declined.'
        )
        core_logic.send_task_decline(
            assignment=assignment,
            _type=assignment_type,
            email_text=request.POST.get('decline-email'),
            sender=request.user,
            request=request,
        )

        return redirect(reverse('user_dashboard'))

    template = 'onetasker/taskhub.html'
    context = {
        'submission': assignment.book,
        'assignment': assignment,
        'send_email': True,
        'center_block': 'onetasker/decline_contact.html',
        'email_text': email_text,
    }

    return render(request, template, context)


@csrf_exempt
def upload(
        request,
        assignment_type,
        assignment_id,
        type_to_handle,
        author=None
):
    assignment = get_assignment(assignment_type, assignment_id)
    book = assignment.book
    _file = upload_receive(request)
    new_file = handle_file(_file, book, type_to_handle, request.user)

    if new_file:
        file_dict = {
            'name': new_file.uuid_filename,
            'size': _file.size,
            'deleteUrl': reverse(
                'assignment_jfu_delete',
                kwargs={
                    'assignment_type': assignment_type,
                    'assignment_id': assignment_id,
                    'file_pk': new_file.pk,
                }
            ),
            'url': reverse(
                'serve_file',
                kwargs={'submission_id': book.id, 'file_id': new_file.pk}
            ),
            'deleteType': 'POST',
            'ruaId': new_file.pk,
            'original_name': new_file.original_filename,
        }
        add_file(assignment, new_file, author)

        return UploadResponse(request, file_dict)

    return HttpResponse('No file')


@csrf_exempt
def upload_author(request, assignment_type, assignment_id, type_to_handle):
    assignment = get_assignment(assignment_type, assignment_id)
    book = assignment.book
    _file = upload_receive(request)
    new_file = handle_file(_file, book, type_to_handle, request.user)

    if new_file:
        file_dict = {
            'name': new_file.uuid_filename,
            'size': _file.size,
            'deleteUrl': reverse(
                'assignment_jfu_delete',
                kwargs={
                    'assignment_type': assignment_type,
                    'assignment_id': assignment_id,
                    'file_pk': new_file.pk,
                }
            ),
            'url': reverse(
                'serve_file',
                kwargs={'submission_id': book.id, 'file_id': new_file.pk}
            ),
            'deleteType': 'POST',
            'ruaId': new_file.pk,
            'original_name': new_file.original_filename,
        }
        add_file(assignment, new_file, True)

        return UploadResponse(request, file_dict)

    return HttpResponse('No file')


@csrf_exempt
def upload_delete(request, assignment_type, assignment_id, file_pk):
    # TODO: refactor duplicate logic
    assignment = get_assignment(assignment_type, assignment_id)
    book = assignment.book
    success = True

    try:
        instance = models.File.objects.get(pk=file_pk)
        default_storage.delete(
            os.path.join(
                settings.BOOK_DIR,
                book.id,
                instance.uuid_filename
            )
        )
        instance.delete()
    except models.File.DoesNotExist:
        success = False

    return JFUResponse(request, success)


def handle_file(file, book, kind, user):
    # TODO: refactor duplicate logic
    if file:
        original_filename = str(
            file._get_name()
        ).replace(
            ',', '_'
        ).replace(
            ';', '_'
        )
        filename = str(uuid4()) + str(os.path.splitext(file._get_name())[1])
        file_mime = mime.guess_type(filename)[0] or 'application/octet-stream'
        file_path = os.path.join(
            settings.BOOK_DIR,
            str(book.id),
            filename,
        )

        with default_storage.open(file_path, 'wb') as file_stream:
            file_stream.write(file.read())

        new_file = models.File(
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
