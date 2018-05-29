import mimetypes as mime
import os
from uuid import uuid4

from django.conf import settings
from django.shortcuts import Http404
from django.utils import timezone
from django.utils.encoding import smart_text

from core import models


def handle_marc21_file(content, name, book, owner):
    original_filename = name
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'books',
        str(book.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')
    fd.write(content)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
        if not file_mime:
            file_mime = 'unknown'
    except IndexError:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'books',
        str(book.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)

    fd.close()
    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
        if not file_mime:
            file_mime = 'unknown'
    except IndexError:
        file_mime = 'unknown'

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

    for chunk in new_file.chunks():
        fd.write(chunk)

    fd.close()
    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
    except IndexError:
        file_mime = 'unknown'

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

    return path


def handle_file(_file, book, kind, owner, label=None):
    original_filename = smart_text(
        _file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'books',
        str(book.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)

    fd.close()
    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
    except IndexError:
        file_mime = 'unknown'

    if not file_mime:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'email',
        'general',
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
    except IndexError:
        file_mime = 'unknown'

    if not file_mime:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'proposals',
        str(proposal_review.proposal.id)
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
    except IndexError:
        file_mime = 'unknown'

    if not file_mime:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'proposals',
        str(proposal.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
    except IndexError:
        file_mime = 'unknown'

    if not file_mime:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'proposals',
        str(proposal.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
    except IndexError:
        file_mime = 'unknown'

    if not file_mime:
        file_mime = 'unknown'

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
    if request.FILES.get('attachment_file'):
        attachment_file = request.FILES.get('attachment_file')
        return handle_file(attachment_file, submission, 'misc', request.user)
    return None


def handle_copyedit_file(_file, book, copyedit, kind):
    original_filename = smart_text(_file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'books',
        str(book.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
        if not file_mime:
            file_mime = 'unknown'
    except IndexError:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'books',
        str(book.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
        if not file_mime:
            file_mime = 'unknown'
    except IndexError:
        file_mime = 'unknown'

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
    folder_structure = os.path.join(
        settings.BASE_DIR,
        'files',
        'books',
        str(book.id),
    )

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in _file.chunks():
        fd.write(chunk)
    fd.close()

    file_mime = mime.guess_type(filename)

    try:
        file_mime = file_mime[0]
        if not file_mime:
            file_mime = 'unknown'
    except IndexError:
        file_mime = 'unknown'

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
