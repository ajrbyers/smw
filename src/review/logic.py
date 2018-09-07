import mimetypes as mime
from os import path, makedirs
from uuid import uuid4

from django.conf import settings
from django.utils.encoding import smart_text

from core import email
from core import models as core_models
from core.setting_util import get_setting


def notify_editors(
        book,
        message,
        book_editors,
        series_editor,
        creator,
        workflow
):
    for editor in book_editors:
        notification = core_models.Task(
            book=book,
            assignee=editor,
            creator=creator,
            text=message,
            workflow=workflow,
        )
        notification.save()

    if series_editor:
        notification = core_models.Task(
            book=book,
            assignee=series_editor,
            creator=creator,
            text=message,
            workflow=workflow,
        )
        notification.save()


def has_additional_files(submission):
    additional_files = [
        _file for _file in submission.files.all() if _file.kind == 'additional'
    ]

    return True if additional_files else False


def handle_review_file(_file, content_type, review_assignment, kind):
    original_filename = smart_text(
        _file._get_name().replace(',', '_').replace(';', '_')
    )
    filename = str(uuid4()) + str(path.splitext(original_filename)[1])

    if content_type == 'book':
        folder_structure = path.join(
            settings.BASE_DIR,
            'files',
            'books',
            str(review_assignment.book.id)
        )
    else:
        folder_structure = path.join(
            settings.BASE_DIR,
            'files',
            'proposals',
            str(review_assignment.proposal.id)
        )

    if not path.exists(folder_structure):
        makedirs(folder_structure)

    _path = path.join(folder_structure, str(filename))
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

    return _path

