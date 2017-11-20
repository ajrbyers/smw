from datetime import datetime

from core import models
from editor import models as editor_models
from revisions import models as revisions_models
from submission import models as submission_models


def author_tasks(user):
    base_url = models.Setting.objects.get(
        group__name='general',
        name='base_url'
    ).value
    task_list = []
    revision_tasks = revisions_models.Revision.objects.filter(
        book__owner=user,
        requested__isnull=False,
        completed__isnull=True,
    ).select_related(
        'book',
    )
    copyedit_tasks = models.CopyeditAssignment.objects.filter(
        book__owner=user,
        author_invited__isnull=False,
        author_completed__isnull=True,
    ).select_related(
        'book',
    )
    typeset_tasks = models.TypesetAssignment.objects.filter(
        book__owner=user,
        author_invited__isnull=False,
        author_completed__isnull=True,
    ).select_related(
        'book',
    )
    proofing_tasks = editor_models.CoverImageProof.objects.filter(
        book__owner=user,
        completed__isnull=True
    ).select_related(
        'book',
    )
    proposal_tasks = submission_models.Proposal.objects.filter(
        owner=user,
        status='revisions_required',
    )

    for revision in revision_tasks:
        task_list.append({
            'type': 'revisions',
            'book': revision.book,
            'task': 'Revisions',
            'date': revision.due,
            'title': revision.book.title,
            'url': '/author/submission/%s/revisions/%s/' % (
                revision.book.id,
                revision.id,
            )
        })

    for copyedit in copyedit_tasks:
        task_list.append({
            'type': 'copyedit',
            'book': copyedit.book,
            'task': 'Copyedit Review',
            'date': copyedit.author_invited,
            'title': copyedit.book.title,
            'url': '/author/submission/%s/editing/copyedit/%s/' % (
                copyedit.book.id,
                copyedit.id,
            )
        })

    for typeset in typeset_tasks:
        task_list.append({
            'type': 'typeset',
            'book': typeset.book,
            'task': 'Typesetting Review',
            'date': typeset.author_invited,
            'title': typeset.book.title,
            'url': '/author/submission/%s/editing/typeset/%s/' % (
                typeset.book.id,
                typeset.id,
            )
        })

    for proof in proofing_tasks:
        task_list.append({
            'type': 'coverimage',
            'book': proof.book,
            'task': 'Cover Image Proof',
            'date': proof.assigned,
            'title': proof.book.title,
            'url': 'http://%s/author/submission/%s/production/#%s' % (
                base_url,
                proof.book.id,
                proof.id
            )
        })

    for proposal in proposal_tasks:
        overdue = False

        if proposal.revision_due_date.date() < datetime.today().date():
            overdue = True

        task_list.append({
            'type': 'proposal',
            'task': 'Proposal Revision',
            'proposal': proposal,
            'overdue': overdue
        })

    return task_list


def submission_tasks(book, user):
    task_list = []
    base_url = models.Setting.objects.get(
        group__name='general',
        name='base_url',
    ).value
    revision_tasks = revisions_models.Revision.objects.filter(
        book=book,
        requested__isnull=False,
        completed__isnull=True,
    )
    copyedit_tasks = models.CopyeditAssignment.objects.filter(
        book=book,
        author_invited__isnull=False,
        author_completed__isnull=True,
    )
    typeset_tasks = models.TypesetAssignment.objects.filter(
        book=book,
        author_invited__isnull=False,
        author_completed__isnull=True,
    )
    proofing_tasks = editor_models.CoverImageProof.objects.filter(
        book=book,
        book__owner=user,
        completed__isnull=True,
    )

    for revision in revision_tasks:
        task_list.append({
            'type': 'revisions',
            'book': revision.book,
            'task': 'Revisions Requested',
            'date': revision.due,
            'title': revision.book.title,
            'url': '/author/submission/%s/revisions/%s/' % (
                book.id,
                revision.id,
            )
        })

    for copyedit in copyedit_tasks:
        task_list.append({
            'type': 'copyedit',
            'book': copyedit.book,
            'task': 'Copyedit Review',
            'date': copyedit.author_invited,
            'title': copyedit.book.title,
            'url': '/author/submission/%s/editing/copyedit/%s/' % (
                copyedit.book.id, copyedit.id
            )
        })

    for typeset in typeset_tasks:
        task_list.append({
            'type': 'typeset',
            'book': typeset.book,
            'task': 'Typesetting Review',
            'date': typeset.author_invited,
            'title': typeset.book.title,
            'url': 'uthor/submission/%s/editing/typeset/%s/' % (
                typeset.book.id, typeset.id
            )
        })

    for proof in proofing_tasks:
        task_list.append({
            'type': 'coverimage',
            'book': proof.book,
            'task': 'Cover Image Proof',
            'date': proof.assigned,
            'title': proof.book.title,
            'url': 'http://%s/author/submission/%s/production/#%s' % (
                base_url,
                proof.book.id,
                proof.id
            )
        })

    return task_list


def check_for_new_messages(user):
    book_list = user.book_set.all()
    messages = models.Message.objects.filter(
        book__in=book_list,
        date_sent__gte=user.last_login,
    )

    return messages
