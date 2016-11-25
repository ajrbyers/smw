from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse, StreamingHttpResponse
from django.conf import settings
from operator import attrgetter
from itertools import chain

import os
import mimetypes
import mimetypes as mime

from uuid import uuid4
from core.files import handle_attachment, handle_file_update, handle_attachment, handle_file
from core import models, log, logic as core_logic, forms as core_forms
from core.decorators import is_editor, is_book_editor, is_book_editor_or_author, is_press_editor
from editor import logic
from revisions import models as revision_models
from review import models as review_models
from manager import models as manager_models, logic as manager_logic
from submission import forms as submission_forms
from editor import forms, models as editor_models
from editorialreview import models as editorial_models


@login_required
@is_editor
def editor_dashboard(request):
    if request.POST:
        order = request.POST.get('order')
        filterby = request.POST.get('filter')
        search = request.POST.get('search')
    else:
        filterby = None
        search = None
        order = 'pk'

    query_list = []

    if filterby:
        if filterby == 'live':
            query_list.append(Q(stage__current_stage__isnull=False))
        elif filterby == 'inprogress':
            query_list.append(Q(stage__current_stage__isnull=True))
        else:
            if not filterby == 'revisions':
                query_list.append(Q(stage__current_stage=filterby))
            else:
                query_list.append(Q(stage__current_stage__isnull=False))

    if search:
        query_list.append(Q(title__contains=search) | Q(subtitle__contains=search) | Q(prefix__contains=search))

    if not 'press-editor' in request.user_roles:
        query_list.append(Q(book_editors__in=[request.user]))

    if query_list:
        list_of_books = models.Book.objects.filter(publication_date__isnull=True).filter(*query_list).exclude(
            stage__current_stage='declined').select_related('stage').select_related('owner__profile').order_by(order)
        book_list = []
        for book in list_of_books:
            if filterby == 'revisions':
                if book.revisions_requested():
                    book_list.append(book)
            else:
                if not book.revisions_requested():
                    book_list.append(book)
    else:
        book_list = models.Book.objects.filter(publication_date__isnull=True).exclude(
            stage__current_stage='declined').select_related('stage').order_by(order)

    series_books = []

    if 'series-editor' in request.user_roles:
        series_books = models.Book.objects.filter(series__editor=request.user).exclude(
            stage__current_stage='declined').select_related('stage').order_by(order)
        for series_book in series_books:
            if series_book not in book_list:
                book_list.append(series_book)

    template = 'editor/dashboard.html'
    context = {
        'book_list': book_list,
        'recent_activity': models.Log.objects.all().order_by('-date_logged')[:15],
        'notifications': models.Task.objects.filter(assignee=request.user, completed__isnull=True).select_related(
            'book').order_by('due'),
        'order': order,
        'filterby': filterby,
    }

    return render(request, template, context)


@login_required
@is_editor
def published_books(request):
    book_list = models.Book.objects.filter(publication_date__isnull=False)

    template = 'editor/published_books.html'
    context = {
        'book_list': book_list,
    }

    return render(request, template, context)


@is_book_editor
def editor_notes(request, submission_id, note_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    notes = models.Note.objects.filter(book=book)
    updated = False

    if note_id:
        note = get_object_or_404(models.Note, book=book, pk=note_id)
        if not note.date_submitted == note.date_last_updated:
            updated = True
    else:
        note = None

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'notes': notes,
        'active': 'user_submission',
        'author_include': 'editor/submission_notes.html',
        'submission_files': 'editor/view_note.html',
        'note_id': note_id,
        'current_note': note,
        'active_page': 'notes',
        'updated': updated,
    }

    return render(request, template, context)


@is_book_editor
def editor_add_note(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    notes = models.Note.objects.filter(book=book)
    note_form = forms.NoteForm()
    if request.POST:
        note_form = forms.NoteForm(request.POST)
        if note_form.is_valid():
            note_form = note_form.save(commit=False)
            note_form.text = request.POST.get("text")
            note_form.user = request.user
            note_form.book = book
            note_form.date_submitted = timezone.now()
            note_form.date_last_updated = timezone.now()
            note_form.save()
            return redirect(reverse('editor_notes', kwargs={'submission_id': book.id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'notes': notes,
        'active': 'user_submission',
        'author_include': 'editor/submission_notes.html',
        'submission_files': 'editor/new_note.html',
        'note_form': note_form,
        'active_page': 'notes',
    }

    return render(request, template, context)


@is_book_editor
def editor_update_note(request, submission_id, note_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    notes = models.Note.objects.filter(book=book)

    note = get_object_or_404(models.Note, book=book, pk=note_id)
    note_form = forms.NoteForm(instance=note)
    if request.POST:
        note_form = forms.NoteForm(request.POST, instance=note)
        if note_form.is_valid():
            note_form.save(commit=False)
            note.text = request.POST.get("text")
            note.user = request.user
            note.date_last_updated = timezone.now()
            note.save()
            return redirect(reverse('editor_notes_view', kwargs={'submission_id': book.id, 'note_id': note_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'notes': notes,
        'active': 'user_submission',
        'author_include': 'editor/submission_notes.html',
        'submission_files': 'editor/new_note.html',
        'note_form': note_form,
        'current_note': note,
        'update': True,
        'active_page': 'notes',
    }

    return render(request, template, context)


@is_book_editor
def editor_submission(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    not_manuscript = True
    not_additional = True
    files = book.files.all()
    for file_check in files:
        if file_check.kind == 'manuscript':
            not_manuscript = False
        elif file_check.kind == 'additional':
            not_additional = False
    template = 'editor/submission.html'
    context = {
        'submission': book,
        'no_additional': not_additional,
        'no_manuscript': not_manuscript,
        'active': 'user_submission',
        'author_include': 'editor/submission_details.html',
        'submission_files': 'editor/submission_files.html',
        'active_page': 'editor_submission',
    }

    return render(request, template, context)


def get_list_of_editors(book):
    book_editors = book.book_editors.all()
    previous_editors = []
    for book_editor in book_editors:
        previous_editors.append(book_editor)
    all_book_editors = User.objects.filter(profile__roles__slug='book-editor')

    list_of_editors = [{} for t in range(0, len(all_book_editors))]
    for t, editor in enumerate(all_book_editors):
        already_added = False
        if editor in previous_editors:
            already_added = True
        list_of_editors[t] = {'editor': editor, 'already_added': already_added,}
    return list_of_editors


def get_list_of_authors(book):
    all_authors = User.objects.filter(profile__roles__slug='author')

    list_of_authors = [{} for t in range(0, len(all_authors))]
    for t, author in enumerate(all_authors):
        owner = False
        if author == book.owner:
            owner = True
        list_of_authors[t] = {'author': author, 'owner': owner,}
    return list_of_authors


def get_list_of_book_authors(book):
    all_authors = book.author.all()

    list_of_authors = [{} for t in range(0, len(all_authors))]
    for t, author in enumerate(all_authors):
        owner = False
        if author.author_email == book.owner.email:
            owner = True
        list_of_authors[t] = {'author': author, 'owner': owner,}
    return list_of_authors


def get_list_of_book_editors(book):
    all_editors = book.editor.all()

    list_of_editors = [{} for t in range(0, len(all_editors))]
    for t, editor in enumerate(all_editors):
        owner = False
        if editor.author_email == book.owner.email:
            owner = True
        list_of_editors[t] = {'editor': editor, 'owner': owner,}
    return list_of_editors


@is_press_editor
def editor_change_owner(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    email_text = models.Setting.objects.get(group__name='email', name='book_editor_ack').value
    book_authors = get_list_of_book_authors(book)
    editors = get_list_of_book_editors(book)
    authors = get_list_of_authors(book)

    if request.GET and "user" in request.GET:
        user_id = request.GET.get("user")
        user = User.objects.get(pk=user_id)
        book.read_only_users.add(book.owner)
        book.owner = user
        book.save()
        authors = get_list_of_authors(book)
        book_authors = get_list_of_book_authors(book)
        editors = get_list_of_book_editors(book)

    elif request.GET:
        type = ""
        if "author" in request.GET:
            user_id = request.GET.get("author")
            type = "Author"
            user = models.Author.objects.get(pk=user_id)
        else:
            user_id = request.GET.get("editor")
            type = "Editor"
            user = models.Editor.objects.get(pk=user_id)

        book.read_only_users.add(book.owner)
        try:
            new_user = User.objects.get(email=user.author_email)
            book.owner = new_user
            book.save()
        except User.DoesNotExist:
            new_pass = manager_logic.generate_password()
            new_user = User.objects.create_user(username=user.author_email,
                                                email=user.author_email,
                                                password=new_pass,
                                                first_name=user.first_name,
                                                last_name=user.last_name)
            messages.add_message(request, messages.SUCCESS,
                                 'Profile created for %s %s, password set to %s.' % (type, new_user.username, new_pass))
            new_profile = models.Profile(middle_name=user.middle_name, salutation=user.salutation,
                                         institution=user.institution,
                                         department=user.department, country=user.country, biography=user.biography,
                                         orcid=user.orcid, twitter=user.twitter, linkedin=user.linkedin,
                                         facebook=user.facebook, user=new_user)
            new_profile.save()
            author_role = get_object_or_404(models.Role, name="Author")
            new_profile.roles.add(author_role)
            new_profile.save()
            book.owner = new_user
            book.save()
            email_text = models.Setting.objects.get(group__name='email', name='new_user_owner_email').value
            logic.send_new_user_ack(book, email_text, new_user, new_pass)

        authors = get_list_of_authors(book)
        book_authors = get_list_of_book_authors(book)
        editors = get_list_of_book_editors(book)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'active': 'user_submission',
        'author_include': 'editor/change_owner.html',
        'submission_files': None,
        'active_page': 'editor_submission',
        'list_of_authors': authors,
        'list_of_editors': editors,
        'book_authors': book_authors,
    }

    return render(request, template, context)


@is_press_editor
def editor_add_editors(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    list_of_editors = get_list_of_editors(book)

    email_text = models.Setting.objects.get(group__name='email', name='book_editor_ack').value

    if request.GET and "add" in request.GET:
        user_id = request.GET.get("add")
        user = User.objects.get(pk=user_id)
        book.book_editors.add(user)
        book.save()
        list_of_editors = get_list_of_editors(book)

    elif request.GET and "remove" in request.GET:
        user_id = request.GET.get("remove")
        user = User.objects.get(pk=user_id)
        book.book_editors.remove(user)
        book.save()
        list_of_editors = get_list_of_editors(book)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'active': 'user_submission',
        'author_include': 'editor/submission_details.html',
        'submission_files': 'editor/add_editors.html',
        'active_page': 'editor_submission',
        'list_of_editors': list_of_editors,
    }

    return render(request, template, context)


@is_book_editor
def editor_tasks(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    tasks = logic.get_submission_tasks(book, request.user)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'active': 'user_submission',
        'author_include': 'shared/tasks.html',
        'tasks': tasks,
        'active_page': 'my_tasks',
    }

    return render(request, template, context)


@is_book_editor
def editor_review(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    review_rounds = models.ReviewRound.objects.filter(book=book).order_by('-round_number')
    editorial_review_assignments = editorial_models.EditorialReview.objects.filter(content_type__model='book', object_id=submission_id).order_by('-pk')

    if request.POST and 'new_round' in request.POST:
        new_round = logic.create_new_review_round(book)
        return redirect(reverse('editor_review_round',
                                kwargs={'submission_id': submission_id, 'round_number': new_round.round_number}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'author_include': 'editor/review_revisions.html',
        'editorial_review_assignments': editorial_review_assignments,
        'review_rounds': review_rounds,
        'revision_requests': revision_models.Revision.objects.filter(book=book, revision_type='review'),
        'active_page': 'editor_review',
    }

    return render(request, template, context)


@is_book_editor
def editor_view_revisions(request, submission_id, revision_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    revision = get_object_or_404(revision_models.Revision, pk=revision_id, completed__isnull=False)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'revision': revision,
        'revision_id': revision.id,
        'active': 'user_submission',
        'author_include': 'editor/submission_details.html',
        'submission_files': 'editor/revisions/view_revisions.html',
        'review_rounds': models.ReviewRound.objects.filter(book=book).order_by('-round_number'),
        'revision_requests': revision_models.Revision.objects.filter(book=book, revision_type='review')
    }

    return render(request, template, context)


@is_book_editor
def editor_review_round(request, submission_id, round_number):
    book = get_object_or_404(models.Book, pk=submission_id)
    review_round = get_object_or_404(models.ReviewRound, book=book, round_number=round_number)
    reviews = models.ReviewAssignment.objects.filter(book=book, review_round__book=book,
                                                     review_round__round_number=round_number)
    review_rounds = models.ReviewRound.objects.filter(book=book).order_by('-round_number')
    internal_review_assignments = models.ReviewAssignment.objects.filter(book=book, review_type='internal',
                                                                         review_round__round_number=round_number).select_related(
        'user', 'review_round')
    external_review_assignments = models.ReviewAssignment.objects.filter(book=book, review_type='external',
                                                                         review_round__round_number=round_number).select_related(
        'user', 'review_round')

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'author_include': 'editor/review_revisions.html',
        'submission_files': 'editor/view_review_round.html',
        'review_round': review_round,
        'review_rounds': review_rounds,
        'round_id': round_number,
        'revision_requests': revision_models.Revision.objects.filter(book=book, revision_type='review'),
        'internal_review_assignments': internal_review_assignments,
        'external_review_assignments': external_review_assignments,
        'editorial_review_assignments': models.EditorialReviewAssignment.objects.filter(book=book).order_by('-pk'),

        'active_page': 'editor_review',
    }

    return render(request, template, context)


@is_book_editor
def editor_review_round_cancel(request, submission_id, round_number):
    book = get_object_or_404(models.Book, pk=submission_id)
    reviews = models.ReviewAssignment.objects.filter(book=book, review_round__book=book,
                                                     review_round__round_number=round_number)
    for review in reviews:
        review.delete()
    logic.cancel_review_round(book)
    return redirect(reverse('editor_review', kwargs={'submission_id': submission_id}))


@is_book_editor
def editor_change_revision_due_date(request, submission_id, revision_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    assignment = revision_models.Revision.objects.get(book=book, pk=revision_id)
    form = forms.ChangeRevisionDueDateForm(instance=assignment)

    if request.method == 'POST':
        form = forms.ChangeRevisionDueDateForm(request.POST, instance=assignment)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Due date updated for revision request {0}: {1}".format(assignment.pk, assignment.due))
            return redirect(reverse('editor_review', kwargs={'submission_id': submission_id}))

    template = 'editor/change_revision_due_date.html'
    context = {
        'form': form,
        'book': book,
    }

    return render(request, template, context)


@is_book_editor
def editorial_review_view(request, submission_id, review_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    review = get_object_or_404(models.EditorialReviewAssignment, book=book, pk=review_id)
    editorial_review_assignments = models.EditorialReviewAssignment.objects.filter(book=book).order_by('-pk')

    if review.editorial_board.filter(pk=request.user.pk).exists():
        member = True
    else:
        member = False

    editorial_board_relations = review_models.FormElementsRelationship.objects.filter(
        form=review.editorial_board_review_form)

    if review.editorial_board_results:
        editorial_board_data_ordered = core_logic.order_data(
            core_logic.decode_json(review.editorial_board_results.data), editorial_board_relations)
    else:
        editorial_board_data_ordered = None

    publication_committee_relations = review_models.FormElementsRelationship.objects.filter(
        form=review.publication_committee_review_form)

    if review.publication_committee_results:
        publication_committee_data_ordered = core_logic.order_data(
            core_logic.decode_json(review.publication_committee_results.data), publication_committee_relations)
    else:
        publication_committee_data_ordered = None

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'editorial_board_member': member,
        'editorial_board_relations': editorial_board_relations,
        'editorial_board_data_ordered': editorial_board_data_ordered,
        'publication_committee_relations': publication_committee_relations,
        'publication_committee_data_ordered': publication_committee_data_ordered,
        'author_include': 'editor/review_revisions.html',
        'submission_files': 'editor/editorial_review.html',
        'revision_requests': revision_models.Revision.objects.filter(book=book, revision_type='review'),
        'editorial_review_assignments': editorial_review_assignments,
        'review_assignment': review,
        'review_rounds': models.ReviewRound.objects.filter(book=book).order_by('-round_number'),
        'active_page': 'editor_review',
    }

    return render(request, template, context)


@is_book_editor
def editorial_review_accept(request, submission_id, review_id, type):
    book = get_object_or_404(models.Book, pk=submission_id)
    review = get_object_or_404(models.EditorialReviewAssignment, book=book, pk=review_id)
    if type == 'editorial':
        review.editorial_board_passed = True
        review.publishing_committee_access_key = uuid4()
        review.save()
    else:
        review.publication_committee_passed = True
        review.completed = timezone.now()
        review.save()

    return redirect(reverse('editorial_review_view', kwargs={'submission_id': submission_id, 'review_id': review.pk}))


@is_book_editor
def remove_assignment_editor(request, submission_id, assignment_type, assignment_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    if assignment_type == 'indexing':
        review_assignment = get_object_or_404(models.IndexAssignment, pk=assignment_id)
    elif assignment_type == 'copyediting':
        review_assignment = get_object_or_404(models.CopyeditAssignment, pk=assignment_id)
    elif assignment_type == 'typesetting':
        review_assignment = get_object_or_404(models.TypesetAssignment, pk=assignment_id)
    else:
        review_assignment = None

    if review_assignment:
        review_assignment.delete()
    if assignment_type == 'typesetting':
        return redirect(reverse('editor_production', kwargs={'submission_id': submission_id,}))
    else:
        return redirect(reverse('editor_editing', kwargs={'submission_id': submission_id,}))


@is_book_editor
def editor_review_round_remove(request, submission_id, round_number, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    review_assignment.delete()

    return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                           'round_number': submission.get_latest_review_round()}))


@is_book_editor
def editor_review_round_withdraw(request, submission_id, round_number, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    if review_assignment.withdrawn:
        review_assignment.withdrawn = False
    else:
        review_assignment.withdrawn = True
    review_assignment.save()

    return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                           'round_number': submission.get_latest_review_round()}))


@is_book_editor
def editor_review_round_reopen(request, submission_id, round_number, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    review_assignment.reopened = True
    review_assignment.save()

    return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                           'round_number': submission.get_latest_review_round()}))


@is_book_editor
def hide_review(request, submission_id, round_id, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    if review_assignment.hide == True:
        review_assignment.hide = False
    else:
        review_assignment.hide = True
    review_assignment.save()
    return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                           'round_number': submission.get_latest_review_round()}))


@is_book_editor
def update_review_due_date(request, submission_id, round_id, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    previous_due_date = review_assignment.due
    if request.POST:
        email_text = models.Setting.objects.get(group__name='email', name='review_due_ack').value
        due_date = request.POST.get('due_date', None)
        notify = request.POST.get('email', None)
        if due_date:
            if not str(due_date) == str(previous_due_date):
                review_assignment.due = due_date
                review_assignment.save()
                if notify:
                    logic.send_review_update(submission, review_assignment, email_text, request.user, attachment=None)
                messages.add_message(request, messages.SUCCESS, 'Due date updated.')
            return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                                   'round_number': submission.get_latest_review_round()}))

    template = 'editor/update_review_due_date.html'
    context = {
        'submission': submission,
        'review': review_assignment,
        'active': 'review',
        'round_id': round_id,
    }

    return render(request, template, context)


@is_book_editor
def update_editorial_review_due_date(request, submission_id, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.EditorialReviewAssignment, pk=review_id)
    previous_due_date = review_assignment.due
    if request.POST:
        email_text = models.Setting.objects.get(group__name='email', name='review_due_ack').value
        due_date = request.POST.get('due_date', None)
        notify = request.POST.get('email', None)
        if due_date:
            if not str(due_date) == str(previous_due_date):
                review_assignment.due = due_date
                review_assignment.save()
                if notify:
                    logic.send_editorial_review_update(submission, review_assignment, email_text, request.user,
                                                       attachment=None)
                messages.add_message(request, messages.SUCCESS, 'Due date updated.')
            return redirect(
                reverse('editorial_review_view', kwargs={'submission_id': submission_id, 'review_id': review_id}))

    template = 'editor/update_editorial_review_due_date.html'
    context = {
        'submission': submission,
        'review': review_assignment,
        'active': 'review',
    }

    return render(request, template, context)


@is_book_editor
def editorial_review_delete(request, submission_id, review_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.EditorialReviewAssignment, pk=review_id)
    review_assignment.delete()
    return redirect(reverse('editor_review', kwargs={'submission_id': book.id}))


@is_book_editor
def editor_editorial_decision(request, submission_id, review_id, decision):
    book = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.EditorialReviewAssignment, pk=review_id)
    review_forms = review_models.Form.objects.all()

    email_text = models.Setting.objects.get(group__name='email', name='editorial_decision_ack').value
    editor_email_text = models.Setting.objects.get(group__name='email', name='production_editor_ack').value
    permission = True

    if request.POST:

        if request.FILES.get('attachment'):
            attachment = handle_file(request.FILES.get('attachment'), book, 'misc', request.user)
        else:
            attachment = None
        if decision == 'revision-editorial':
            messages.add_message(request, messages.SUCCESS, 'Submission declined.')
            if 'inform' in request.POST:
                url = "%s/review/submission/%s/access_key/%s/" % (
                request.META['HTTP_HOST'], book.pk, review_assignment.editorial_board_access_key)
                core_logic.send_editorial_decision_ack(review_assignment=review_assignment, contact="editorial-board",
                                                       decision="Revision Required",
                                                       email_text=request.POST.get('id_email_text'),
                                                       attachment=attachment)
            return redirect(reverse('editorial_review_view', kwargs={'submission_id': book.id, 'review_id': review_id}))

        elif decision == 'revision-publishing':

            messages.add_message(request, messages.SUCCESS, 'Submission has been moved to the review stage.')
            if 'inform' in request.POST:
                url = "%s/review/submission/%s/access_key/%s/" % (
                request.META['HTTP_HOST'], book.pk, review_assignment.publishing_committee_access_key)
                core_logic.send_editorial_decision_ack(review_assignment=review_assignment,
                                                       contact="publishing-committee", decision="Revision Required",
                                                       email_text=request.POST.get('id_email_text'),
                                                       attachment=attachment)
            return redirect(reverse('editorial_review_view', kwargs={'submission_id': book.id, 'review_id': review_id}))

        elif decision == 'invite-publishing':
            review_assignment.editorial_board_passed = True
            review_assignment.publishing_committee_access_key = uuid4()
            review_assignment.publication_committee_review_form = review_models.Form.objects.get(
                ref=request.POST.get('review_form'))
            review_assignment.save()
            if 'inform' in request.POST:
                url = "%s/review/editorial/%s/access_key/%s/" % (
                request.META['HTTP_HOST'], book.pk, review_assignment.publishing_committee_access_key)
                core_logic.send_editorial_decision_ack(review_assignment=review_assignment,
                                                       contact="publishing-committee",
                                                       decision="Invitation to Editorial Review",
                                                       email_text=request.POST.get('id_email_text'),
                                                       attachment=attachment, url=url)
            return redirect(reverse('editorial_review_view', kwargs={'submission_id': book.id, 'review_id': review_id}))

        elif decision == 'send-decision':
            review_assignment.publication_committee_passed = True
            review_assignment.completed = timezone.now()
            review_assignment.save()
            author_decision = request.POST.get('recommendation')

            if author_decision == 'accept':
                if not book.stage.editing:
                    log.add_log_entry(book=book, user=request.user, kind='editing',
                                      message='Submission moved to Editing.', short_name='Submission in Editing')
                book.stage.editing = timezone.now()
                book.stage.current_stage = 'editing'
                book.stage.save()
            elif author_decision == 'decline':
                book.stage.declined = timezone.now()
                book.stage.current_stage = 'declined'
                book.stage.save()
                messages.add_message(request, messages.SUCCESS, 'Submission declined.')
            elif author_decision == 'revisions':
                core_logic.send_editorial_decision_ack(review_assignment=review_assignment, contact="author",
                                                       decision=request.POST.get('recommendation'),
                                                       email_text=request.POST.get('id_email_text'),
                                                       attachment=attachment)
                return redirect(reverse('request_revisions', kwargs={'submission_id': book.id, 'returner': 'review'}))

            if 'inform' in request.POST:
                core_logic.send_editorial_decision_ack(review_assignment=review_assignment, contact="author",
                                                       decision=request.POST.get('recommendation'),
                                                       email_text=request.POST.get('id_email_text'),
                                                       attachment=attachment)
            return redirect(reverse('editorial_review_view', kwargs={'submission_id': book.id, 'review_id': review_id}))

    template = 'editor/editorial-decisions.html'
    context = {
        'submission': book,
        'decision': decision,
        'email_text': email_text,
        'editor_email_text': editor_email_text,
        'permission': permission,
        'review_forms': review_forms,
    }

    return render(request, template, context)


@is_book_editor
def editor_decision(request, submission_id, decision):
    book = get_object_or_404(models.Book, pk=submission_id)
    email_text = models.Setting.objects.get(group__name='email', name='decision_ack').value
    editor_email_text = models.Setting.objects.get(group__name='email', name='production_editor_ack').value
    permission = True

    if book.stage.current_stage == 'editing':
        production_editors = User.objects.filter(profile__roles__slug='production-editor')
    else:
        production_editors = None

    if book.stage.current_stage == 'declined':
        permission = False
    if decision == 'decline':
        if book.stage.current_stage == 'editing':
            permission = False
    elif decision == 'review':
        if book.stage.current_stage == 'review' or book.stage.current_stage == 'editing':
            permission = False
    elif decision == 'editing' and book.stage.current_stage == 'editing':
        permission = False
    elif decision == 'production':
        if book.stage.current_stage == 'review' or book.stage.current_stage == 'production':
            permission = False

    if request.POST:

        if request.FILES.get('attachment'):
            attachment = handle_file(request.FILES.get('attachment'), book, 'misc', request.user)
        else:
            attachment = None
        if decision == 'decline':
            book.stage.declined = timezone.now()
            book.stage.current_stage = 'declined'
            book.stage.save()
            messages.add_message(request, messages.SUCCESS, 'Submission declined.')
            if 'inform' in request.POST:
                core_logic.send_decision_ack(book=book, decision=decision, email_text=request.POST.get('id_email_text'),
                                             attachment=attachment)
            elif 'skip' in request.POST:
                print "Skip"
            return redirect(reverse('editor_dashboard'))

        elif decision == 'review':
            core_logic.create_new_review_round(book)
            book.stage.review = timezone.now()
            book.stage.current_stage = 'review'
            book.stage.save()

            if book.stage.current_stage == 'review':
                log.add_log_entry(book=book, user=request.user, kind='review', message='Submission moved to Review',
                                  short_name='Submission in Review')

            messages.add_message(request, messages.SUCCESS, 'Submission has been moved to the review stage.')
            if 'inform' in request.POST:
                core_logic.send_decision_ack(book=book, decision=decision, email_text=request.POST.get('id_email_text'),
                                             attachment=attachment)
            elif 'skip' in request.POST:
                print "Skip"

            return redirect(reverse('editor_review', kwargs={'submission_id': book.id}))

        elif decision == 'editing':
            if not book.stage.editing:
                log.add_log_entry(book=book, user=request.user, kind='editing', message='Submission moved to Editing.',
                                  short_name='Submission in Editing')
            book.stage.editing = timezone.now()
            book.stage.current_stage = 'editing'
            book.stage.save()
            if 'inform' in request.POST:
                if 'include_url' in request.POST and request.POST['include_url'] == 'on':
                    url = "%s/author/submission/%s/review/" % (request.META['HTTP_HOST'], book.pk)
                else:
                    url = None
                core_logic.send_decision_ack(book=book, decision=decision, email_text=request.POST.get('id_email_text'),
                                             attachment=attachment, url=url)
            elif 'skip' in request.POST:
                print "Skip"
            return redirect(reverse('editor_editing', kwargs={'submission_id': submission_id}))

        elif decision == 'production':
            if not book.stage.production:
                log.add_log_entry(book=book, user=request.user, kind='production',
                                  message='Submission moved to Production', short_name='Submission in Production')
            book.stage.production = timezone.now()
            book.stage.current_stage = 'production'
            book.stage.save()
            if 'inform' in request.POST:
                core_logic.send_decision_ack(book=book, decision=decision, email_text=request.POST.get('id_email_text'),
                                             attachment=attachment)
                production_editor_list = User.objects.filter(pk__in=request.POST.getlist('production_editor'))
                for editor in production_editor_list:
                    core_logic.send_production_editor_ack(book, editor, request.POST.get('id_editor_email_text'),
                                                          attachment)
                    log.add_log_entry(book=book, user=request.user, kind='production',
                                      message='Production Editor %s %s assigend to %s' % (
                                      editor.first_name, editor.last_name, book.title),
                                      short_name='Production Editor Assigned')

            elif 'skip' in request.POST:
                print "Skip"
            return redirect(reverse('editor_production', kwargs={'submission_id': submission_id}))

    template = 'editor/decisions.html'
    context = {
        'submission': book,
        'decision': decision,
        'email_text': email_text,
        'editor_email_text': editor_email_text,
        'permission': permission,
        'production_editors': production_editors,
    }

    return render(request, template, context)


@is_book_editor
def request_revisions(request, submission_id, returner):
    book = get_object_or_404(models.Book, pk=submission_id)
    email_text = models.Setting.objects.get(group__name='email', name='request_revisions').value
    form = forms.RevisionForm()

    if revision_models.Revision.objects.filter(book=book, completed__isnull=True, revision_type=returner):
        messages.add_message(request, messages.WARNING,
                             'There is already an outstanding revision request for this book.')

    if request.POST:
        form = forms.RevisionForm(request.POST)
        if form.is_valid():
            new_revision_request = form.save(commit=False)
            new_revision_request.book = book
            new_revision_request.revision_type = returner
            new_revision_request.requestor = request.user
            new_revision_request.save()

            email_text = request.POST.get('id_email_text')
            attachment_files = request.FILES.getlist('attachment')
            attachments = []

            if attachment_files:
                for attachment in attachment_files:
                    attachment = handle_file(attachment, book, 'other', request.user,
                                             "Attachment: Uploaded by %s" % (request.user.username))
                    attachments.append(attachment)

            logic.send_requests_revisions(book, request.user, new_revision_request, email_text, attachments)
            log.add_log_entry(book, request.user, 'revisions', '%s %s requested revisions for %s' % (
            request.user.first_name, request.user.last_name, book.title), 'Revisions Requested')

            if returner == 'review':
                return redirect(reverse('editor_review', kwargs={'submission_id': submission_id}))
            else:
                messages.add_message(request, messages.INFO, 'Revision request submitted')
                return redirect(reverse('editor_submission', kwargs={'submission_id': submission_id}))

    template = 'editor/revisions/request_revisions.html'
    context = {
        'submission': book,
        'form': form,
        'email_text': email_text,
    }

    return render(request, template, context)


@is_book_editor
def add_review_files(request, submission_id, review_type):
    submission = get_object_or_404(models.Book, pk=submission_id)

    if request.POST:
        files = models.File.objects.filter(pk__in=request.POST.getlist('file'))
        for file in files:
            if review_type == 'internal':
                submission.internal_review_files.add(file)
            else:
                submission.external_review_files.add(file)

        messages.add_message(request, messages.SUCCESS, '%s files added to Review' % files.count())

        return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                               'round_number': submission.get_latest_review_round()}))

    template = 'editor/add_review_files.html'
    context = {
        'submission': submission,
    }

    return render(request, template, context)


@is_book_editor
def editor_add_editorial_reviewers(request, submission_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    editors = models.User.objects.filter(
        Q(profile__roles__slug='press-editor') | Q(profile__roles__slug='book-editor') | Q(
            profile__roles__slug='production-editor')).distinct()
    review_forms = review_models.Form.objects.all()
    committees = manager_models.Group.objects.filter(group_type='editorial_group')

    if request.POST and "add_user" in request.POST:
        messages.add_message(request, messages.WARNING, 'Select an "editor" role in order to be able to add this user')
        return redirect("%s?return=%s" % (reverse('add_user'), reverse('editor_add_reviewers',
                                                                       kwargs={'submission_id': submission_id,
                                                                               'review_type': review_type,
                                                                               'round_number': round_number})))

    elif request.POST:
        editors = User.objects.filter(pk__in=request.POST.getlist('editor'))
        committees = manager_models.Group.objects.filter(pk__in=request.POST.getlist('committee'))
        review_form = review_models.Form.objects.get(ref=request.POST.get('review_form'))
        due_date = request.POST.get('due_date')
        email_text = request.POST.get('message')

        if request.FILES.get('attachment'):
            attachment = handle_file(request.FILES.get('attachment'), submission, 'misc', request.user)
        else:
            attachment = None

        # Handle reviewers
        assignment = logic.handle_editorial_review_assignment(request, submission, editors, uuid4(), due_date,
                                                              request.user, email_text, attachment)

        # Handle committees
        for committee in committees:
            members = manager_models.GroupMembership.objects.filter(group=committee)
            logic.handle_editorial_review_assignment(request, submission, members, due_date, request.user, email_text,
                                                     attachment)

        # Tidy up and save
        submission.stage.editorial_review = timezone.now()
        submission.stage.save()
        log.add_log_entry(book=submission, user=request.user, kind='review', message='Editorial Review Started',
                          short_name='Submission entered Editorial Review')

        assignment.editorial_board_review_form = review_form
        assignment.save()

        return redirect(
            reverse('editorial_review_view', kwargs={'submission_id': submission_id, 'review_id': assignment.pk}))

    template = 'editor/add_editors_editorial_review.html'
    context = {
        'editors': editors,
        'committees': committees,
        'active': 'new',
        'email_text': models.Setting.objects.get(group__name='email', name='review_request'),
        'review_forms': review_forms,

        'submission': submission,
    }

    return render(request, template, context)


@is_book_editor
def editor_add_reviewers(request, submission_id, review_type, round_number):
    submission = get_object_or_404(models.Book, pk=submission_id)
    reviewers = models.User.objects.filter(profile__roles__slug='reviewer')
    review_forms = review_models.Form.objects.all()
    committees = manager_models.Group.objects.filter(group_type='review_committee')
    review_round = get_object_or_404(models.ReviewRound, book=submission, round_number=round_number)

    if request.POST and "add_user" in request.POST:
        messages.add_message(request, messages.WARNING,
                             'Select the "Reviewer" role in order to be able to add this user')
        return redirect("%s?return=%s" % (reverse('add_user'), reverse('editor_add_reviewers',
                                                                       kwargs={'submission_id': submission_id,
                                                                               'review_type': review_type,
                                                                               'round_number': round_number})))

    elif request.POST:
        reviewers = User.objects.filter(pk__in=request.POST.getlist('reviewer'))
        committees = manager_models.Group.objects.filter(pk__in=request.POST.getlist('committee'))
        review_form = review_models.Form.objects.get(ref=request.POST.get('review_form'))
        due_date = request.POST.get('due_date')
        email_text = request.POST.get('message')

        if request.FILES.get('attachment'):
            attachment = handle_file(request.FILES.get('attachment'), submission, 'misc', request.user)
        else:
            attachment = None

        if 'access_key' in request.POST:
            generate = True
        else:
            generate = False
        # Handle reviewers
        for reviewer in reviewers:
            if generate:
                access_key = uuid4()
                logic.handle_review_assignment(request, submission, reviewer, review_type, due_date, review_round,
                                               request.user, email_text, review_form, attachment, access_key=access_key)
            else:
                logic.handle_review_assignment(request, submission, reviewer, review_type, due_date, review_round,
                                               request.user, email_text, review_form, attachment)

        # Handle committees
        for committee in committees:
            members = manager_models.GroupMembership.objects.filter(group=committee)
            for member in members:
                if generate:
                    access_key = uuid4()
                    logic.handle_review_assignment(request, submission, member.user, review_type, due_date,
                                                   review_round, request.user, email_text, review_form, attachment,
                                                   access_key=access_key)
                else:
                    logic.handle_review_assignment(request, submission, member.user, review_type, due_date,
                                                   review_round, request.user, email_text, review_form, attachment)

        # Tidy up and save
        if review_type == 'internal' and not submission.stage.internal_review:
            submission.stage.internal_review = timezone.now()
            submission.stage.save()
            log.add_log_entry(book=submission, user=request.user, kind='review', message='Internal Review Started',
                              short_name='Submission entered Internal Review')

        elif review_type == 'external' and not submission.stage.external_review:
            submission.stage.external_review = timezone.now()
            submission.stage.save()
            log.add_log_entry(book=submission, user=request.user, kind='review', message='External Review Started',
                              short_name='Submission entered External Review')

        submission.review_form = review_form
        submission.save()

        return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                               'round_number': submission.get_latest_review_round()}))

    template = 'editor/add_reviewers.html'
    context = {
        'reviewers': reviewers,
        'committees': committees,
        'active': 'new',
        'email_text': models.Setting.objects.get(group__name='email', name='review_request'),
        'review_forms': review_forms,

        'submission': submission,
    }

    return render(request, template, context)


@is_book_editor
def editor_review_assignment(request, submission_id, round_id, review_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    review_assignment = get_object_or_404(models.ReviewAssignment, pk=review_id)
    review_rounds = models.ReviewRound.objects.filter(book=submission).order_by('-round_number')
    result = review_assignment.results
    relations = review_models.FormElementsRelationship.objects.filter(form=result.form)
    data_ordered = core_logic.order_data(core_logic.decode_json(result.data), relations)

    template = 'editor/submission.html'
    context = {
        'author_include': 'editor/review_revisions.html',
        'submission_files': 'shared/view_review.html',
        'submission': submission,
        'review': review_assignment,
        'data_ordered': data_ordered,
        'result': result,
        'active': 'review',
        'review_rounds': review_rounds,
        'revision_requests': revision_models.Revision.objects.filter(book=submission, revision_type='review'),
    }

    return render(request, template, context)


@is_book_editor
def editor_editing(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    if request.POST and request.GET.get('start', None):
        action = request.GET.get('start')

        if action == 'copyediting':
            book.stage.copyediting = timezone.now()
            log.add_log_entry(book=book, user=request.user, kind='editing', message='Copyediting has commenced.',
                              short_name='Copyediting Started')
        elif action == 'indexing':
            book.stage.indexing = timezone.now()
            log.add_log_entry(book=book, user=request.user, kind='editing', message='Indexing has commenced.',
                              short_name='Indexing Started')
        book.stage.save()
        return redirect(reverse('editor_editing', kwargs={'submission_id': submission_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'author_include': 'editor/editing.html',
        'active_page': 'editing',
    }

    return render(request, template, context)


@is_book_editor
def editor_production(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    if request.POST and request.GET.get('start', None):
        if request.GET.get('start') == 'typesetting':
            book.stage.typesetting = timezone.now()
            book.stage.save()

    template = 'editor/submission.html'
    context = {
        'author_include': 'editor/production/view.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'physical_list': models.PhysicalFormat.objects.filter(book=book),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def editor_publish(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    if not book.stage.publication:
        book.stage.publication = timezone.now()
        book.stage.current_stage = 'published'
        book.stage.save()
        if not book.publication_date:
            book.publication_date = timezone.now()
        book.save()
        messages.add_message(request, messages.SUCCESS, 'Book has successfully been published')
    else:
        messages.add_message(request, messages.INFO, 'Book is already published')

    return redirect(reverse('editor_submission', kwargs={'submission_id': submission_id}))


@is_book_editor
def catalog(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    internal_review_assignments = models.ReviewAssignment.objects.filter(book=book, review_type='internal',
                                                                         completed__isnull=False).select_related('user',
                                                                                                                 'review_round')
    external_review_assignments = models.ReviewAssignment.objects.filter(book=book, review_type='external',
                                                                         completed__isnull=False).select_related('user',
                                                                                                                 'review_round')
    metadata_form = forms.EditMetadata(instance=book)
    cover_form = forms.CoverForm(instance=book)

    if request.POST:
        if request.GET.get('metadata', None):
            metadata_form = forms.EditMetadata(request.POST, instance=book)

            if metadata_form.is_valid():
                metadata_form.save()

                for keyword in book.keywords.all():
                    book.keywords.remove(keyword)

                for keyword in request.POST.get('tags').split(','):
                    new_keyword, c = models.Keyword.objects.get_or_create(name=keyword)
                    book.keywords.add(new_keyword)

                for subject in book.subject.all():
                    book.subject.remove(subject)

                for subject in request.POST.get('stags').split(','):
                    new_subject, c = models.Subject.objects.get_or_create(name=subject)
                    book.subject.add(new_subject)

                book.save()
                return redirect(reverse('catalog', kwargs={'submission_id': submission_id}))
            else:
                print metadata_form.errors

        if request.GET.get('cover', None):
            cover_form = forms.CoverForm(request.POST, request.FILES, instance=book)

            if cover_form.is_valid():
                cover_form.save()
                return redirect(reverse('catalog', kwargs={'submission_id': submission_id}))

        if request.GET.get('invite_author', None):
            note_to_author = request.POST.get('author_invite', None)
            new_cover_proof = editor_models.CoverImageProof(book=book, editor=request.user,
                                                            note_to_author=note_to_author)
            new_cover_proof.save()
            log.add_log_entry(book=book, user=request.user, kind='production',
                              message='%s %s requested Cover Image Proofs' % (
                              request.user.first_name, request.user.last_name), short_name='Cover Image Proof Request')
            messages.add_message(request, messages.SUCCESS, 'Cover Image Proof request added.')
            return redirect(reverse('catalog', kwargs={'submission_id': submission_id}))

    template = 'editor/catalog/catalog.html'
    context = {
        'active': 'production',
        'submission': book,
        'metadata_form': metadata_form,
        'cover_form': cover_form,
        'internal_review_assignments': internal_review_assignments,
        'external_review_assignments': external_review_assignments,
        'active_page': 'catalog_view',
    }

    return render(request, template, context)


@is_book_editor
def catalog_marc21(request, submission_id, type=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    content_preloaded = None

    if type:
        if type == 'xml':
            content_preloaded = core_logic.book_to_mark21_file_content(book, request.user, True)
        else:
            content_preloaded = core_logic.book_to_mark21_file_content(book, request.user)

    marc21_form = forms.Marc21Form()

    if request.POST:
        if request.FILES:
            uploaded_file = request.FILES.get('format_file')
            content_preloaded = ""
            for chunk in uploaded_file.chunks():
                content_preloaded = content_preloaded + chunk
        else:
            if 'xml-download' in request.POST:
                file_pk = core_logic.book_to_mark21_file_download_content(book, request.user,
                                                                          request.POST.get('file_content'), True)
            else:
                file_pk = core_logic.book_to_mark21_file_download_content(book, request.user,
                                                                          request.POST.get('file_content'))
            _file = get_object_or_404(models.File, pk=file_pk)
            file_path = os.path.join(settings.BOOK_DIR, submission_id, _file.uuid_filename)

            try:
                fsock = open(file_path, 'r')
                mimetype = mimetypes.guess_type(file_path)
                response = StreamingHttpResponse(fsock, content_type=mimetype)
                response['Content-Disposition'] = "attachment; filename=%s" % (_file.original_filename)
                # log.add_log_entry(book=book, user=request.user, kind='file', message='File %s downloaded.' % _file.uuid_filename, short_name='Download')
                return response
            except IOError:
                messages.add_message(request, messages.ERROR, 'File not found. %s' % (file_path))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    template = 'editor/catalog/catalog_marc21.html'
    context = {
        'active': 'production',
        'submission': book,
        'marc21_form': marc21_form,
        'active_page': 'catalog_view',
        'content_preloaded': content_preloaded,
    }

    return render(request, template, context)


@is_book_editor
def identifiers(request, submission_id, identifier_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    digital_format_choices = logic.generate_digital_choices(book.format_set.all())
    physical_format_choices = logic.generate_physical_choices(book.physicalformat_set.all())

    if identifier_id:
        identifier = get_object_or_404(models.Identifier, pk=identifier_id)

        if request.GET.get('delete', None) == 'true':
            identifier.delete()
            return redirect(reverse('identifiers', kwargs={'submission_id': submission_id}))

        form = forms.IdentifierForm(instance=identifier, digital_format_choices=digital_format_choices,
                                    physical_format_choices=physical_format_choices)
    else:
        identifier = None
        form = forms.IdentifierForm(digital_format_choices=digital_format_choices,
                                    physical_format_choices=physical_format_choices)

    if request.POST:
        if identifier_id:
            form = forms.IdentifierForm(request.POST, instance=identifier)
        else:
            form = forms.IdentifierForm(request.POST)

        if form.is_valid():
            new_identifier = form.save(commit=False)
            new_identifier.book = book
            new_identifier.save()
        else:
            print form.errors

            return redirect(reverse('identifiers', kwargs={'submission_id': submission_id}))

    template = 'editor/catalog/identifiers.html'
    context = {
        'submission': book,
        'identifier': identifier,
        'form': form,
        'active_page': 'catalog_view',
    }

    return render(request, template, context)


@is_book_editor
def update_contributor(request, submission_id, contributor_type, contributor_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    active = 'add'
    if contributor_id:
        active = 'edit'
        if contributor_type == 'author':
            contributor = get_object_or_404(models.Author, pk=contributor_id)
            form = submission_forms.AuthorForm(instance=contributor)
        elif contributor_type == 'editor':
            contributor = get_object_or_404(models.Editor, pk=contributor_id)
            form = submission_forms.EditorForm(instance=contributor)
    else:
        active = 'add'
        contributor = None
        if contributor_type == 'author':
            form = submission_forms.AuthorForm()
        elif contributor_type == 'editor':
            form = submission_forms.EditorForm()

    if request.POST:
        if contributor:
            if contributor_type == 'author':
                form = submission_forms.AuthorForm(request.POST, instance=contributor)
            elif contributor_type == 'editor':
                form = submission_forms.EditorForm(request.POST, instance=contributor)
        else:
            if contributor_type == 'author':
                form = submission_forms.AuthorForm(request.POST)
            elif contributor_type == 'editor':
                form = submission_forms.EditorForm(request.POST)

        if form.is_valid():
            saved_contributor = form.save()

            if not contributor:
                if contributor_type == 'author':
                    book.author.add(saved_contributor)
                elif contributor_type == 'editor':
                    book.editor.add(saved_contributor)

            return redirect(reverse('catalog', kwargs={'submission_id': submission_id}))

    template = 'editor/catalog/update_contributor.html'
    context = {
        'submission': book,
        'form': form,
        'contributor': contributor,
        'type': contributor_type,
        'active': active,
        'active_page': 'catalog_view',
    }

    return render(request, template, context)


@is_book_editor
def delete_contributor(request, submission_id, contributor_type, contributor_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    if contributor_id:
        if contributor_type == 'author':
            contributor = get_object_or_404(models.Author, pk=contributor_id)
            messages.add_message(request, messages.ERROR, 'User %s has been deleted.' % (contributor.full_name))
            book.author.remove(contributor)
        elif contributor_type == 'editor':
            contributor = get_object_or_404(models.Editor, pk=contributor_id)
            book.editor.remove(contributor)
        book.save()
        contributor.delete()

        return redirect(reverse('catalog', kwargs={'submission_id': submission_id}))


@is_book_editor
def add_format(request, submission_id, file_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    if file_id:
        exist_file = get_object_or_404(models.File, pk=file_id)
        format_form = core_forms.FormatFormInitial()
    else:
        exist_file = None
        format_form = core_forms.FormatForm()

    if request.POST:
        if file_id:
            format_form = core_forms.FormatFormInitial(request.POST)
        else:
            format_form = core_forms.FormatForm(request.POST, request.FILES)

        if format_form.is_valid():
            if file_id:
                new_file = None
            else:
                new_file = handle_file(request.FILES.get('format_file'), book, 'format', request.user)
            new_format = format_form.save(commit=False)
            new_format.book = book
            label = request.POST.get('file_label')
            if new_file:
                if label:
                    new_file.label = label
                else:
                    new_file.label = None
                new_file.save()
                new_format.file = new_file
            else:
                new_file = exist_file
                new_file.pk = None
                new_file.label = label
                new_file.save()
                new_format.file = new_file
            new_format.save()
            log.add_log_entry(book=book, user=request.user, kind='production',
                              message='%s %s loaded a new format, %s' % (
                              request.user.first_name, request.user.last_name, new_format.identifier),
                              short_name='New Format Loaded')
            return redirect(reverse('editor_production', kwargs={'submission_id': book.id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'format_form': format_form,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/add_format.html',
        'active': 'production',
        'submission': book,
        'existing_file': exist_file,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def add_chapter(request, submission_id, chapter_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    if chapter_id:
        exist_chapter = get_object_or_404(models.Chapter, pk=file_id)
        chapter_form = core_forms.ChapterFormInitial()
    else:
        exist_chapter = None
        chapter_form = core_forms.ChapterForm()

    if request.POST:
        chapter_form = core_forms.ChapterFormInitial(request.POST)

        if chapter_form.is_valid():
            new_chapter = chapter_form.save(commit=False)
            new_chapter.book = book
            new_chapter.save()
            for keyword in request.POST.get('tags').split(','):
                new_keyword, c = models.Keyword.objects.get_or_create(name=keyword)
                new_chapter.keywords.add(new_keyword)
            for subject in request.POST.get('stags').split(','):
                new_subject, c = models.Subject.objects.get_or_create(name=subject)
                new_chapter.disciplines.add(new_subject)
            new_chapter.save()
            log.add_log_entry(book=book, user=request.user, kind='production',
                              message='%s %s loaded a new chapter, %s' % (
                              request.user.first_name, request.user.last_name, new_chapter.sequence),
                              short_name='New Chapter Loaded')
            return redirect(
                reverse('editor_view_chapter', kwargs={'submission_id': book.id, 'chapter_id': new_chapter.id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'chapter_form': chapter_form,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/add_chapter.html',
        'active': 'production',
        'submission': book,
        'exist_chapter': exist_chapter,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def view_chapter(request, submission_id, chapter_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    chapter_formats = models.ChapterFormat.objects.filter(chapter=chapter)

    if request.POST and 'remove_author' in request.POST:
        author_id = request.POST.get('author_id')[:-1]
        author = models.Author.objects.get(pk=author_id)
        chapter.authors.remove(author)

        return redirect(reverse('editor_view_chapter', kwargs={'submission_id': book.id, 'chapter_id': chapter.id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'chapter': chapter,
        'chapter_formats': chapter_formats,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/view_chapter.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def update_chapter(request, submission_id, chapter_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    chapter_formats = models.ChapterFormat.objects.filter(chapter=chapter)

    chapter_form = core_forms.ChapterForm(instance=chapter)

    if request.POST:
        chapter_form = core_forms.ChapterForm(request.POST)

        if chapter_form.is_valid():
            new_chapter = chapter_form.save(commit=False)
            chapter.sequence = new_chapter.sequence
            chapter.blurbs = new_chapter.blurbs
            chapter.name = new_chapter.name
            chapter.doi = new_chapter.doi

            for keyword in chapter.keywords.all():
                chapter.keywords.remove(keyword)

            for subject in chapter.disciplines.all():
                chapter.disciplines.remove(subject)

            chapter.save()
            for keyword in request.POST.get('tags').split(','):
                new_keyword, c = models.Keyword.objects.get_or_create(name=keyword)
                chapter.keywords.add(new_keyword)
            for subject in request.POST.get('stags').split(','):
                new_subject, c = models.Subject.objects.get_or_create(name=subject)
                chapter.disciplines.add(new_subject)
            chapter.save()
            log.add_log_entry(book=book, user=request.user, kind='production', message='%s %s updated a chapter, %s' % (
            request.user.first_name, request.user.last_name, chapter.sequence), short_name='New Chapter Loaded')
            return redirect(reverse('editor_view_chapter', kwargs={'submission_id': book.id, 'chapter_id': chapter_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'chapter_form': chapter_form,
        'update': True,
        'chapter': chapter,
        'chapter_formats': chapter_formats,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/view_chapter.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def view_chapter_format(request, submission_id, chapter_id, format_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    chapter_format = get_object_or_404(models.ChapterFormat, chapter=chapter, pk=format_id)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'chapter': chapter,
        'chapter_format': chapter_format,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/view_chapter_format.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def add_chapter_format(request, submission_id, chapter_id, file_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    if file_id:
        exist_file = get_object_or_404(models.File, pk=file_id)
        chapter_form = core_forms.ChapterFormatForm()
    else:
        exist_file = None
        chapter_form = core_forms.ChapterFormatForm()

    if request.POST:
        if file_id:
            chapter_form = core_forms.ChapterFormatForm(request.POST)
        else:
            chapter_form = core_forms.ChapterFormatForm(request.POST, request.FILES)

        if chapter_form.is_valid():
            if file_id:
                new_file = None
            else:
                new_file = handle_file(request.FILES.get('chapter_file'), book, 'chapter', request.user)
            new_chapter_format = chapter_form.save(commit=False)
            new_chapter_format.chapter = chapter
            new_chapter_format.book = book
            label = request.POST.get('file_label')
            if new_file:
                if label:
                    new_file.label = label
                else:
                    new_file.label = None
                new_file.save()
                new_chapter_format.file = new_file
            else:
                new_file = exist_file
                new_file.pk = None
                new_file.label = label
                new_file.save()
                new_chapter_format.file = new_file
            new_chapter_format.save()
            chapter.formats.add(new_chapter_format)
            chapter.save()
            log.add_log_entry(book=book, user=request.user, kind='production',
                              message='%s %s loaded a new chapter, %s' % (
                              request.user.first_name, request.user.last_name, new_chapter_format.identifier),
                              short_name='New Chapter Loaded')
            return redirect(reverse('editor_view_chapter', kwargs={'submission_id': book.id, 'chapter_id': chapter_id}))
        else:
            print chapter_form.errors

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'chapter': chapter,
        'chapter_form': chapter_form,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/add_chapter_format.html',
        'active': 'production',
        'existing_file': exist_file,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def add_chapter_author(request, submission_id, chapter_id, author_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)

    if author_id:
        author = get_object_or_404(models.Author, pk=author_id)
        form = submission_forms.AuthorForm(instance=author)
    else:
        author = None
        form = submission_forms.AuthorForm()

    if request.POST:

        if author_id:
            form = submission_forms.AuthorForm(request.POST, instance=author)
            message = 'Author edited.'
        else:
            form = submission_forms.AuthorForm(request.POST)
            message = 'Author added.'

        if form.is_valid():
            new_chapter_author = form.save()
            chapter.authors.add(new_chapter_author)

            messages.add_message(request, messages.INFO, message)

        return redirect(reverse('editor_view_chapter', kwargs={'submission_id': book.id, 'chapter_id': chapter_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'chapter': chapter,
        'active': 'production',
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/add_chapter_author.html',
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'form': form,
    }

    return render(request, template, context)


@is_book_editor
def add_physical(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    format_form = forms.PhysicalFormatForm()
    if request.POST:
        format_form = forms.PhysicalFormatForm(request.POST, request.FILES)
        if format_form.is_valid():
            new_format = format_form.save(commit=False)
            new_format.book = book
            new_format.save()
            log.add_log_entry(book=book, user=request.user, kind='production',
                              message='%s %s loaded a new format, %s' % (
                              request.user.first_name, request.user.last_name, new_format.name),
                              short_name='New Format Loaded')
            return redirect(reverse('editor_production', kwargs={'submission_id': book.id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'physical_form': format_form,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/physical_format.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def delete_format_or_chapter(request, submission_id, format_or_chapter, id):
    book = get_object_or_404(models.Book, pk=submission_id)

    if format_or_chapter == 'chapter':
        item = get_object_or_404(models.Chapter, pk=id)
    elif format_or_chapter == 'format':
        item = get_object_or_404(models.Format, pk=id)

    if item:
        item.file.delete()
        item.delete()
        messages.add_message(request, messages.SUCCESS, 'Item deleted')
    else:
        messages.add_message(request, messages.WARNING, 'Item not found.')

    return redirect(reverse('editor_production', kwargs={'submission_id': book.id}))


@is_book_editor
def update_format_or_chapter(request, submission_id, format_or_chapter, id):
    book = get_object_or_404(models.Book, pk=submission_id)
    chapter = None
    if format_or_chapter == 'chapter':
        item = get_object_or_404(models.ChapterFormat, pk=id)
        chapter = item.chapter
        type = 'chapter'
    elif format_or_chapter == 'format':
        item = get_object_or_404(models.Format, pk=id)
        type = 'format'
    file = item.file
    form = forms.UpdateChapterFormat()

    if request.POST:
        form = forms.UpdateChapterFormat(request.POST, request.FILES)
        if form.is_valid():
            item.name = request.POST.get('name')
            item.identifier = request.POST.get('identifier')
            file_type = request.POST.get('file_type')
            item.save()
            file_update = item.file
            label = request.POST.get('file_label')
            if label:
                file_update.label = label
            else:
                file_update.label = None
            file_update.save()
            if request.FILES:
                print request.FILES
                if type == 'chapter':
                    if file_type:
                        item.file_type = file_type
                        item.save()
                    handle_file_update(request.FILES.get('chapter_file'), file_update, book, item.file.kind,
                                       request.user)
                else:
                    handle_file_update(request.FILES.get('chapter_file'), file_update, book, item.file.kind, request.user)
            return redirect(reverse('editor_production', kwargs={'submission_id': book.id}))

    template = 'editor/submission.html'
    context = {
        'item': item,
        'form': form,
        'type': type,
        'file': file,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/update.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def assign_typesetter(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    typesetters = models.User.objects.filter(profile__roles__slug='typesetter')

    if request.POST:
        typesetter_list = User.objects.filter(pk__in=request.POST.getlist('typesetter'))
        file_list = models.File.objects.filter(pk__in=request.POST.getlist('file'))
        due_date = request.POST.get('due_date')
        email_text = request.POST.get('message')

        attachment = handle_attachment(request, book)

        for typesetter in typesetter_list:
            logic.handle_typeset_assignment(request, book, typesetter, file_list, due_date, email_text,
                                            requestor=request.user, attachment=attachment)

        return redirect(reverse('editor_production', kwargs={'submission_id': submission_id}))

    template = 'editor/submission.html'
    context = {
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/assign_typesetter.html',
        'active': 'production',
        'submission': book,
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'typesetters': typesetters,
        'active_page': 'production',
        'email_text': models.Setting.objects.get(group__name='email', name='typeset_request'),
    }

    return render(request, template, context)


@is_book_editor
def view_typesetter(request, submission_id, typeset_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    typeset = get_object_or_404(models.TypesetAssignment, pk=typeset_id)
    email_text = models.Setting.objects.get(group__name='email', name='author_typeset_request').value

    author_form = forms.TypesetAuthorInvite(instance=typeset)
    if typeset.editor_second_review:
        author_form = forms.TypesetTypesetterInvite(instance=typeset)
        email_text = models.Setting.objects.get(group__name='email', name='typesetter_typeset_request').value

    if request.POST and 'invite_author' in request.POST:
        if not typeset.completed:
            messages.add_message(request, messages.WARNING,
                                 'This typeset has not been completed, you cannot invite the author to review.')
            return redirect(
                reverse('view_typesetter', kwargs={'submission_id': submission_id, 'typeset_id': typeset_id}))
        else:
            typeset.editor_review = timezone.now()
            typeset.save()

    elif request.POST and 'invite_typesetter' in request.POST:
        typeset.editor_second_review = timezone.now()
        typeset.save()
        return redirect(reverse('view_typesetter', kwargs={'submission_id': submission_id, 'typeset_id': typeset_id}))

    elif request.POST and 'send_invite_typesetter' in request.POST:
        author_form = forms.TypesetTypesetterInvite(request.POST, instance=typeset)
        if author_form.is_valid():
            author_form.save()
            typeset.typesetter_invited = timezone.now()
            typeset.save()
            email_text = request.POST.get('email_text')
            logic.send_invite_typesetter(book, typeset, email_text, request.user)
        return redirect(reverse('view_typesetter', kwargs={'submission_id': submission_id, 'typeset_id': typeset_id}))

    elif request.POST and 'send_invite_author' in request.POST:
        author_form = forms.TypesetAuthorInvite(request.POST, instance=typeset)
        if author_form.is_valid():
            author_form.save()
            typeset.author_invited = timezone.now()
            typeset.save()
            email_text = request.POST.get('email_text')
            logic.send_invite_typesetter(book, typeset, email_text, request.user)
        return redirect(reverse('view_typesetter', kwargs={'submission_id': submission_id, 'typeset_id': typeset_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/view_typeset.html',
        'active': 'production',
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'typeset': typeset,
        'typeset_id': typeset.id,
        'author_form': author_form,
        'email_text': email_text,
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def view_typesetter_alter_due_date(request, submission_id, typeset_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    typeset = get_object_or_404(models.TypesetAssignment, pk=typeset_id)
    email_text = models.Setting.objects.get(group__name='email', name='author_typeset_request').value

    date_form = forms.TypesetDate(instance=typeset)

    if request.POST:
        date_form = forms.TypesetDate(request.POST, instance=typeset)
        if date_form.is_valid():
            date_form.save()
            typeset.save()
        # email_text = request.POST.get('email_text')
        #	logic.send_invite_typesetter(book, typeset, email_text, request.user)
        return redirect(reverse('view_typesetter', kwargs={'submission_id': submission_id, 'typeset_id': typeset_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/view_typeset_due_date.html',
        'active': 'production',
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'typeset': typeset,
        'typeset_id': typeset.id,
        'date_form': date_form,
        'email_text': email_text,
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def view_typesetter_alter_author_due(request, submission_id, typeset_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    typeset = get_object_or_404(models.TypesetAssignment, pk=typeset_id)
    email_text = models.Setting.objects.get(group__name='email', name='author_typeset_request').value

    date_form = forms.TypesetAuthorDate(instance=typeset)

    if request.POST:
        date_form = forms.TypesetAuthorDate(request.POST, instance=typeset)
        if date_form.is_valid():
            date_form.save()
            typeset.save()
        # email_text = request.POST.get('email_text')
        #	logic.send_invite_typesetter(book, typeset, email_text, request.user)
        return redirect(reverse('view_typesetter', kwargs={'submission_id': submission_id, 'typeset_id': typeset_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'author_date': True,
        'author_include': 'editor/production/view.html',
        'submission_files': 'editor/production/view_typeset_due_date.html',
        'active': 'production',
        'format_list': models.Format.objects.filter(book=book).select_related('file'),
        'chapter_list': models.Chapter.objects.filter(book=book).order_by('sequence'),
        'typeset': typeset,
        'typeset_id': typeset.id,
        'date_form': date_form,
        'email_text': email_text,
        'active_page': 'production',
    }

    return render(request, template, context)


@is_book_editor
def retailers(request, submission_id, retailer_id=None):
    book = get_object_or_404(models.Book, pk=submission_id)
    retailers = models.Retailer.objects.filter(book=book)
    form = forms.RetailerForm()

    if retailer_id:
        retailer = get_object_or_404(models.Retailer, pk=retailer_id)
        form = forms.RetailerForm(instance=retailer)

    if request.GET.get('delete', None):
        retailer.delete()
        return redirect(reverse('retailers', kwargs={'submission_id': submission_id}))

    if request.POST:
        if retailer_id:
            form = forms.RetailerForm(request.POST, instance=retailer)
            message = 'Retailer updated.'
        else:
            form = forms.RetailerForm(request.POST)
            message = 'New retailer added.'

        if form.is_valid():
            new_retailer = form.save(commit=False)
            new_retailer.book = book
            new_retailer.save()

            messages.add_message(request, messages.INFO, message)

            return redirect(reverse('retailers', kwargs={'submission_id': submission_id}))

    template = 'editor/catalog/retailers.html'
    context = {
        'submission': book,
        'retailers': retailers,
        'form': form,
        'retailer_id': retailer_id,
        'active_page': 'catalog_view',
    }

    return render(request, template, context)


@is_book_editor
def decline_submission(request, submission_id):
    submission = get_object_or_404(models.Book, pk=submission_id)

    if request.POST and 'decline' in request.POST:
        submission.stage.declined = timezone.now()
        submission.stage.current_stage = 'declined'
        submission.stage.save()
        messages.add_message(request, messages.SUCCESS, 'Submission declined.')
        return redirect(reverse('editor_dashboard'))

    template = 'editor/decline_submission.html'
    context = {
        'submission': submission,
    }

    return render(request, template, context)


@is_book_editor
def delete_review_files(request, submission_id, review_type, file_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    file = get_object_or_404(models.File, pk=file_id)

    if review_type == 'internal':
        submission.internal_review_files.remove(file)
    else:
        submission.external_review_files.remove(file)

    return redirect(reverse('editor_review_round', kwargs={'submission_id': submission_id,
                                                           'round_number': submission.get_latest_review_round()}))


@is_book_editor
def editor_status(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'active': 'user_submission',
        'active_page': 'status',
        'author_include': 'shared/status.html',
        'submission_files': 'shared/messages.html',
        'timeline': core_logic.build_time_line(book),
    }

    return render(request, template, context)


@is_book_editor
def assign_copyeditor(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    copyeditors = models.User.objects.filter(profile__roles__slug='copyeditor')

    if not book.stage.current_stage == 'editing':
        messages.add_message(request, messages.WARNING,
                             'You cannot assign a Copyeditor, this book is not in the Editing phase.')
        return redirect(reverse('editor_editing', kwargs={'submission_id': book.id}))

    if request.POST:
        copyeditor_list = User.objects.filter(pk__in=request.POST.getlist('copyeditor'))
        file_list = models.File.objects.filter(pk__in=request.POST.getlist('file'))
        due_date = request.POST.get('due_date')
        email_text = request.POST.get('message')
        note = request.POST.get('note')
        attachment = handle_attachment(request, book)

        for copyeditor in copyeditor_list:
            logic.handle_copyeditor_assignment(request, book, copyeditor, file_list, due_date, note, email_text,
                                               requestor=request.user, attachment=attachment)
            log.add_log_entry(book=book, user=request.user, kind='editing',
                              message='Copyeditor %s %s assigend to %s' % (
                              copyeditor.first_name, copyeditor.last_name, book.title),
                              short_name='Copyeditor Assigned')

        return redirect(reverse('editor_editing', kwargs={'submission_id': submission_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'copyeditors': copyeditors,
        'author_include': 'editor/editing.html',
        'submission_files': 'editor/assign_copyeditor.html',
        'email_text': models.Setting.objects.get(group__name='email', name='copyedit_request'),
        'active_page': 'editing',
    }

    return render(request, template, context)


@is_book_editor
def view_copyedit(request, submission_id, copyedit_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    copyedit = get_object_or_404(models.CopyeditAssignment, pk=copyedit_id)
    author_form = core_forms.CopyeditAuthorInvite(instance=copyedit)
    email_text = models.Setting.objects.get(group__name='email', name='author_copyedit_request').value

    if request.POST and 'invite_author' in request.POST:
        if not copyedit.completed:
            messages.add_message(request, messages.WARNING,
                                 'This copyedit has not been completed, you cannot invite the author to review.')
            return redirect(
                reverse('view_copyedit', kwargs={'submission_id': submission_id, 'copyedit_id': copyedit_id}))
        else:
            copyedit.editor_review = timezone.now()
            log.add_log_entry(book=book, user=request.user, kind='editing',
                              message='Copyedit Review Completed by %s %s' % (
                              request.user.first_name, request.user.last_name),
                              short_name='Editor Copyedit Review Complete')
            copyedit.save()

    elif request.POST and 'send_invite_author' in request.POST:

        attachment = handle_attachment(request, book)

        author_form = core_forms.CopyeditAuthorInvite(request.POST, instance=copyedit)
        author_form.save()
        copyedit.author_invited = timezone.now()
        copyedit.save()
        email_text = request.POST.get('email_text')
        logic.send_author_invite(book, copyedit, email_text, request.user, attachment)
        return redirect(reverse('view_copyedit', kwargs={'submission_id': submission_id, 'copyedit_id': copyedit_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'copyedit': copyedit,
        'author_form': author_form,
        'author_include': 'editor/editing.html',
        'submission_files': 'editor/view_copyedit.html',
        'email_text': email_text,
        'timeline': core_logic.build_time_line_editing_copyedit(copyedit),
        'active_page': 'editing',
    }

    return render(request, template, context)


@is_book_editor
def assign_indexer(request, submission_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    indexers = models.User.objects.filter(profile__roles__slug='indexer')

    if not book.stage.current_stage == 'editing':
        messages.add_message(request, messages.WARNING,
                             'You cannot assign an Indexer, this book is not in the Editing phase.')
        return redirect(reverse('editor_editing', kwargs={'submission_id': book.id}))

    if request.POST:
        indexer_list = User.objects.filter(pk__in=request.POST.getlist('indexer'))
        file_list = models.File.objects.filter(pk__in=request.POST.getlist('file'))
        due_date = request.POST.get('due_date')
        email_text = request.POST.get('message')
        note = request.POST.get('note')
        attachment = handle_attachment(request, book)

        for indexer in indexer_list:
            logic.handle_indexer_assignment(request, book, indexer, file_list, due_date, note, email_text,
                                            requestor=request.user, attachment=attachment)
            log.add_log_entry(book=book, user=request.user, kind='editing', message='Indexer %s %s assigend to %s' % (
            indexer.first_name, indexer.last_name, book.title), short_name='Indexer Assigned')

        return redirect(reverse('editor_editing', kwargs={'submission_id': submission_id}))

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'indexers': indexers,
        'author_include': 'editor/editing.html',
        'submission_files': 'editor/assign_indexer.html',
        'email_text': models.Setting.objects.get(group__name='email', name='index_request'),
        'active_page': 'editing',

    }

    return render(request, template, context)


@is_book_editor
def view_index(request, submission_id, index_id):
    book = get_object_or_404(models.Book, pk=submission_id)
    index = get_object_or_404(models.IndexAssignment, pk=index_id)

    template = 'editor/submission.html'
    context = {
        'submission': book,
        'index': index,
        'author_include': 'editor/editing.html',
        'submission_files': 'editor/view_index.html',
        'timeline': core_logic.build_time_line_editing_indexer(index),
        'active_page': 'editing',

    }

    return render(request, template, context)


## CONTRACTS ##

@is_book_editor
def contract_manager(request, submission_id, contract_id=None):
    submission = get_object_or_404(models.Book, pk=submission_id)
    action = 'normal'
    if contract_id:
        new_contract_form = forms.UploadContract(instance=submission.contract)
        action = 'edit'
    else:
        new_contract_form = forms.UploadContract()

    if request.POST:

        if contract_id:
            submission.contract.title = request.POST.get('title')
            submission.contract.notes = request.POST.get('notes')
            date = request.POST.get('editor_signed_off')

            if '/' in str(date):
                editor_date = date[6:] + '-' + date[3:5] + '-' + date[:2]
                submission.contract.editor_signed_off = editor_date
            else:
                submission.contract.editor_signed_off = date

            date = str(request.POST.get('author_signed_off'))

            if '/' in str(date):
                author_date = date[6:] + '-' + date[3:5] + '-' + date[:2]
                submission.contract.author_signed_off = author_date
            else:
                submission.contract.author_signed_off = date

            if 'contract_file' in request.FILES:
                author_file = request.FILES.get('contract_file')
                new_file = handle_file(author_file, submission, 'contract', request.user)
                submission.contract.editor_file = new_file

            submission.contract.save()
            submission.save()
            return redirect(reverse('contract_manager', kwargs={'submission_id': submission.id}))
        else:
            new_contract_form = forms.UploadContract(request.POST, request.FILES)
            if new_contract_form.is_valid():
                new_contract = new_contract_form.save(commit=False)
                if 'contract_file' in request.FILES:
                    author_file = request.FILES.get('contract_file')
                    new_file = handle_file(author_file, submission, 'contract', request.user)

                    new_contract.editor_file = new_file
                    new_contract.save()
                    submission.contract = new_contract
                    submission.save()

                    if not new_contract.author_signed_off:
                        email_text = models.Setting.objects.get(group__name='email',
                                                                name='contract_author_sign_off').value
                        logic.send_author_sign_off(submission, email_text, sender=request.user)

                    return redirect(reverse('contract_manager', kwargs={'submission_id': submission.id}))
                else:
                    messages.add_message(request, messages.ERROR, 'You must upload a contract file.')

    template = 'editor/contract/contract_manager.html'
    context = {
        'submission': submission,
        'new_contract_form': new_contract_form,
        'action': action,
    }

    return render(request, template, context)


## END CONTRACTS ##

### WORKFLOW NEW SUBMISSIONS 

@is_editor
def new_submissions(request):
    submission_list = models.Book.objects.filter(stage__current_stage='submission')

    template = 'editor/new_submissions.html'
    context = {
        'submission_list': submission_list,
        'active': 'new',
    }

    return render(request, template, context)


@is_book_editor
def view_new_submission(request, submission_id):
    submission = get_object_or_404(models.Book, pk=submission_id)

    if request.POST and 'review' in request.POST:
        logic.create_new_review_round(submission)
        submission.stage.review = timezone.now()
        submission.stage.current_stage = 'review'
        submission.stage.save()

        if submission.stage.current_stage == 'review':
            log.add_log_entry(book=submission, user=request.user, kind='review', message='Submission moved to Review',
                              short_name='Submission in Review')

        messages.add_message(request, messages.SUCCESS, 'Submission has been moved to the review stage.')

        return redirect(reverse('editor_review', kwargs={'submission_id': submission.id}))

    template = 'editor/new/view_new_submission.html'
    context = {
        'submission': submission,
        'active': 'new',
        'revision_requests': revision_models.Revision.objects.filter(book=submission, revision_type='submission')
    }

    return render(request, template, context)


@is_editor
def files_for_production(request, submission_id):
    submission = get_object_or_404(models.Book, pk=submission_id)
    files = submission.files.all()
    internal_review_files = submission.internal_review_files.all()
    external_review_files = submission.external_review_files.all()
    misc_files = submission.misc_files.all()
    manuscript_files = files.filter(kind='manuscript')
    production_files = submission.production_files.order_by('kind')

    copyedit_files = [x for copyedit in submission.copyeditassignment_set.all()
                      for x in chain(copyedit.copyedit_files.all(),  copyedit.author_files.all())]

    index_files = [x for index in submission.indexassignment_set.all() for x in index.index_files.all()]

    #'Primary Files' formed of manuscript, copyedit and index files, excluding those already in production_files.
    primary_files = sorted(
        set(chain(manuscript_files, copyedit_files, index_files)) - set(production_files),
        key=attrgetter('date_uploaded'), reverse=True
        )

    #All files associated with book, excluding those already in primary files and production files, sorted by type.
    additional_files = sorted(
        set(chain(files, internal_review_files, external_review_files, misc_files))
        - set(primary_files) - set(production_files),
        key=attrgetter('kind')
    )

    # Pre-populate production_files with most recently modified primary file, run only once so user can remove it.
    if submission.first_run == True:
        submission.production_files.add(primary_files[0])
        submission.first_run = False
        submission.save()

    #Handle adding and removing files to production_files list
    if request.POST:
        if 'add_file' in request.POST:
            file_id = request.POST.get('file_id')[:-1] #[:-1] to ignore trailing slash
            file = models.File.objects.get(pk=file_id)
            submission.production_files.add(file)

        if 'remove_file' in request.POST:
            file_id = request.POST.get('file_id')[:-1] #[:-1] to ignore trailing slash
            file = models.File.objects.get(pk=file_id)
            submission.production_files.remove(file)

        return redirect(reverse('files_for_production', kwargs={'submission_id': submission.id}))

    template = 'editor/submission.html'
    context = {
        'submission': submission,
        'files': files,
        'production_files': production_files,
        'primary_files': primary_files,
        'additional_files': additional_files,
        'author_include': 'editor/file_list.html',
        'submission_files': 'editor/files_for_production.html'
    }

    return render(request, template, context)
