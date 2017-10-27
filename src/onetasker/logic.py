from django.shortcuts import Http404
from django.shortcuts import get_object_or_404

from core import files, models, task
import forms

from datetime import datetime


def get_assignment(assignment_type, assignment_id):
    ''' given one of the 3 assignment types and it's id it returns an Assignment object'''

    if assignment_type == 'copyedit':
        assignment = get_object_or_404(models.CopyeditAssignment,
                                       pk=assignment_id)
    elif assignment_type == 'typesetting':
        assignment = get_object_or_404(models.TypesetAssignment,
                                       pk=assignment_id)
    elif assignment_type == 'indexing':
        assignment = get_object_or_404(models.IndexAssignment, pk=assignment_id)
    else:
        raise Http404

    return assignment


def get_assignemnt_form(request, assignment_type, assignment):
    if assignment_type == 'copyedit':
        form = forms.Copyedit(request.POST, instance=assignment)
    elif assignment_type == 'typesetting':
        form = forms.Typeset(request.POST, instance=assignment)
    elif assignment_type == 'indexing':
        form = forms.Index(request.POST, instance=assignment)
    else:
        raise Http404

    return form


def get_unposted_form(request, assignment_type, assignment):
    if assignment_type == 'copyedit':
        form = forms.Copyedit(instance=assignment)
    elif assignment_type == 'typesetting':
        form = forms.Typeset(instance=assignment)
    elif assignment_type == 'indexing':
        form = forms.Index(instance=assignment)
    else:
        raise Http404

    return form


def handle_files(assignment, files):
    for _file in files:
        new_file = handle_file(_file, assignment)
        assignment = add_file(assignment, new_file)
    assignment = complete_task(assignment)

    return assignment


def handle_file(_file, assignment):
    if assignment.type() == 'copyedit':
        handled_file = files.handle_onetasker_file(_file, assignment.book,
                                                   assignment, 'copyedit')
    elif assignment.type() == 'typesetting':
        handled_file = files.handle_onetasker_file(_file, assignment.book,
                                                   assignment, 'typeset')
    elif assignment.type() == 'indexing':
        handled_file = files.handle_onetasker_file(_file, assignment.book,
                                                   assignment, 'index')
    else:
        raise Http404

    return handled_file


def add_file(assignment, new_file, author=None):
    if assignment.type() == 'copyedit':
        if author:
            assignment.author_files.add(new_file)
        else:
            assignment.copyedit_files.add(new_file)
    elif assignment.type() == 'typesetting':
        if assignment.state().get('state') == 'typesetter_second':
            assignment.typesetter_files.add(new_file)
        else:
            assignment.typeset_files.add(new_file)
            return assignment
    elif assignment.type() == 'indexing':
        assignment.index_files.add(new_file)

    return assignment


def complete_task(assignment):
    if assignment.type() == 'copyedit':
        assignment.completed = datetime.now()
    elif assignment.type() == 'typesetting':
        if assignment.state().get('state') == 'typesetter_second':
            assignment.typesetter_completed = datetime.now()
        else:
            assignment.completed = datetime.now()
    elif assignment.type() == 'indexing':
        assignment.completed = datetime.now()

    return assignment


def right_block(assignment):
    if assignment.completed:
        right_block = 'onetasker/elements/completed.html'
        if assignment.type() == 'typesetting' and not assignment.typesetter_completed and assignment.state().get(
                'state') == 'typesetter_second':
            right_block = 'onetasker/elements/task_form.html'
    elif assignment.accepted:
        right_block = 'onetasker/elements/task_form.html'
    else:
        right_block = None

    return right_block


def notify_editor(assignment, text):
    if assignment.type() == 'copyedit':
        assignee = assignment.copyeditor
    elif assignment.type() == 'typesetting':
        assignee = assignment.typesetter
    elif assignment.type() == 'indexing':
        assignee = assignment.indexer

    return task.create_new_task(assignment.book, assignment.requestor, assignee,
                                text, assignment.type())


def get_submitted_files(assignment):
    if assignment.type() == 'copyedit':
        files = assignment.copyedit_files.all()
    elif assignment.type() == 'typesetting':
        if assignment.state().get('state') == 'typesetter_second':
            files = assignment.typesetter_files.all()
        else:
            files = assignment.typeset_files.all()
    elif assignment.type() == 'indexing':
        files = assignment.index_files.all()
    return files
