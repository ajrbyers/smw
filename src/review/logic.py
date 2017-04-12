import os
import mimetypes as mime
from uuid import uuid4


from django.utils.encoding import smart_text
from django.conf import settings

from core import models as core_models

def get_editors(review_assignment):
    press_editors = review_assignment.book.press_editors.all()
    book_editors = review_assignment.book.book_editors.all()

    if review_assignment.book.series:
        series_editor = review_assignment.book.series.editor

        if series_editor:
            series_editor_list = [{'editor': series_editor, 'isSeriesEditor': True}]
            press_editor_list = [{'editor': editor, 'isSeriesEditor': False} for editor in press_editors if not editor == series_editor_list[0]['editor']]
        else:
            series_editor_list = []
            press_editor_list = [{'editor': editor, 'isSeriesEditor': False} for editor in press_editors]

    else:
        series_editor_list = []
        press_editor_list = [{'editor': editor, 'isSeriesEditor': False} for editor in press_editors]

    if book_editors:
        book_editor_list = [{'editor': editor, 'isSeriesEditor': False} for editor in book_editors if not editor in press_editors]
    else:
        book_editor_list = []

    return (press_editor_list + series_editor_list + book_editor_list)

def notify_editors(book, message, editors, creator, workflow):

    for editor_details in editors:
        notification = core_models.Task(book=book, assignee=editor_details['editor'], creator=creator, text=message, workflow=workflow)
        notification.save()

def has_additional_files(submission):
    additional_files = [_file for _file in submission.files.all() if _file.kind == 'additional']
    return True if additional_files else False

def handle_review_file(file, review_assignment, kind):
    original_filename = smart_text(file._get_name())
    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    folder = "{0}s".format(review_assignment.content_type)
    folder_structure = os.path.join(settings.BASE_DIR, 'files', folder, str(review_assignment.content_object.id))

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

    return path
