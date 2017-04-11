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
