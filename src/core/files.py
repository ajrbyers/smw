import mimetypes as mime
import os
from uuid import uuid4

from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import Http404
from django.utils import timezone
from django.utils.encoding import smart_text

from core import models


def handle_marc21_file(content, name, book, owner):
    original_filename = name
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'

    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(content)

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind='marc21',
        owner=owner,
    )
    new_file.save()

    return new_file


def handle_onetasker_file(_file, book, assignment, kind):
    original_filename = smart_text(_file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    owner = get_owner(assignment)
    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        owner=owner,
    )
    new_file.save()

    return new_file


def handle_file_update(new_file, old_file, book, owner, label=None):
    original_filename = smart_text(
        new_file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(new_file.read)

    new_version = models.FileVersion(
        file=old_file,
        original_filename=old_file.original_filename,
        uuid_filename=old_file.uuid_filename,
        date_uploaded=old_file.date_uploaded,
        owner=old_file.owner,
    )
    new_version.save()

    old_file.mime_type = file_mime
    old_file.original_filename = original_filename
    old_file.uuid_filename = filename
    old_file.date_uploaded = timezone.now()
    old_file.owner = owner

    if label:
        old_file.label = label

    old_file.save()

    return file_path


def handle_file(_file, book, kind, owner, label=None):
    original_filename = smart_text(
        _file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )
    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        label=label,
        owner=owner,
    )
    new_file.save()

    return new_file


def handle_email_file(_file, kind, owner, label=None):
    original_filename = smart_text(_file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.EMAIL_DIR,
        str(filename),
    )
    file_path = os.path.join(file_path, )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        label=label,
        owner=owner,
    )
    new_file.save()

    return new_file


def handle_multiple_email_files(request_files, file_owner):
    """Processes in-memory files from a HTTP response and returns saved files.

    Args:
        request_files (list): in-memory files from a Django http response.
        file_owner (django.contrib.auth.models.User): owner of the saved files.

    Returns:
        list: file objects that can be sent as email attachments.

    """
    attachments = []
    for request_file in request_files:
        attachment = handle_email_file(
            _file=request_file,
            kind='other',
            owner=file_owner,
            label="Attachment: Uploaded by {username}".format(
                username=file_owner.username
            )
        )
        attachments.append(attachment)

    return attachments


def handle_proposal_review_file(
        _file,
        proposal_review,
        kind,
        owner,
        label=None
):
    original_filename = smart_text(
        _file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.PROPOSAL_DIR,
        str(proposal_review.proposal.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        label=label,
        owner=owner,
    )
    new_file.save()

    return new_file


def handle_proposal_file(_file, proposal, kind, owner, label=None):
    original_filename = smart_text(
        _file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.PROPOSAL_DIR,
        str(proposal.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        label=label,
        owner=owner,
    )
    new_file.save()

    return new_file


def handle_proposal_file_form(_file, proposal, kind, owner, label=None):
    original_filename = smart_text(_file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.PROPOSAL_DIR,
        str(proposal.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        label=label,
        owner=owner,
    )
    new_file.save()

    return new_file.pk


def handle_attachment(request, submission):
    attachment_file = request.FILES.get('attachment_file')
    if attachment_file:
        return handle_email_file(attachment_file, 'misc', request.user)
    return None


def handle_copyedit_file(_file, book, copyedit, kind):
    original_filename = smart_text(_file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        owner=copyedit.copyeditor,
    )
    new_file.save()

    return new_file


def handle_index_file(_file, book, index, kind):
    original_filename = smart_text(_file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        owner=index.indexer,
    )
    new_file.save()

    return new_file


def handle_typeset_file(_file, book, typeset, kind):
    original_filename = smart_text(
        _file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    file_mime = mime.guess_type(filename)[0] or 'unknown/unknown'
    file_path = os.path.join(
        settings.BOOK_DIR,
        str(book.id),
        str(filename),
    )

    with default_storage.open(file_path, 'wb') as file_stream:
        file_stream.write(_file.read())

    new_file = models.File(
        mime_type=file_mime,
        original_filename=original_filename,
        uuid_filename=filename,
        stage_uploaded=1,
        kind=kind,
        owner=typeset.typesetter,
    )
    new_file.save()

    return new_file


def get_owner(assignment):
    if assignment.type() == 'copyedit':
        return assignment.copyeditor
    elif assignment.type() == 'typesetting':
        return assignment.typesetter
    elif assignment.type() == 'indexing':
        return assignment.indexer

    raise Http404
