from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect

from core import models as core_models
from core.decorators import is_press_editor
from core.files import handle_file
from editor import forms as editor_forms
from submission import forms as submission_forms
from swiftsubmit import forms


@is_press_editor
def index(request):

    metadata_form = editor_forms.EditMetadata()

    if request.POST:
        metadata_form = editor_forms.EditMetadata(request.POST)

        if metadata_form.is_valid():
            book = metadata_form.save()

            for keyword in book.keywords.all():
                book.keywords.remove(keyword)

            for keyword in request.POST.get('tags').split(','):
                new_keyword, c = core_models.Keyword.objects.get_or_create(
                    name=keyword,
                )
                book.keywords.add(new_keyword)

            for subject in book.subject.all():
                book.subject.remove(subject)

            for subject in request.POST.get('stags').split(','):
                new_subject, c = core_models.Subject.objects.get_or_create(
                    name=subject
                )
                book.subject.add(new_subject)

            book.save()

            return redirect(
                reverse('swiftsubmit_formats', kwargs={'book_id': book.pk})
            )

    template = 'swiftsubmit/index.html'
    context = {'metadata_form': metadata_form}

    return render(request, template, context)


@is_press_editor
def formats(request, book_id):

    book = get_object_or_404(core_models.Book, pk=book_id)
    format_form = editor_forms.FormatForm(instance=book)

    if request.POST and 'new_format' in request.POST:
        format_form = editor_forms.FormatForm(request.POST, request.FILES)

        if format_form.is_valid():
            new_file = handle_file(
                request.FILES.get('format_file'),
                book,
                'format',
                request.user,
            )
            new_file.label = request.POST.get('label')
            new_format = format_form.save(commit=False)
            new_format.book = book
            new_format.file = new_file
            new_format.save()

            return redirect(reverse(
                'swiftsubmit_formats',
                kwargs={'book_id': book.pk}
            ))

    elif request.POST and 'next_step' in request.POST:
        if book.book_type == 'monograph':
            return redirect(
                reverse('swiftsubmit_authors', kwargs={'book_id': book.pk})
            )
        else:
            return redirect(
                reverse('swiftsubmit_editors', kwargs={'book_id': book.pk})
            )

    template = 'swiftsubmit/formats.html'
    context = {
        'submission': book,
        'format_form': format_form,
        'format_list': core_models.Format.objects.filter(
            book=book
        ).select_related(
            'file'
        ),
        'active': 'ssp',
    }

    return render(request, template, context)


@is_press_editor
def author(request, book_id, author_id=None):

    book = get_object_or_404(core_models.Book, pk=book_id)

    if request.GET.get('delete'):
        author = get_object_or_404(
            core_models.Author, pk=request.GET.get('delete')
        )
        author.delete()

        return redirect(
            reverse('swiftsubmit_authors', kwargs={'book_id': book.id})
        )

    if author_id:
        if book.author.filter(pk=author_id).exists():
            author = get_object_or_404(core_models.Author, pk=author_id)
            author_form = submission_forms.AuthorForm(instance=author)
        else:
            return HttpResponseForbidden()
    else:
        author = None
        author_form = submission_forms.AuthorForm()

    if request.method == 'POST':
        if author:
            author_form = submission_forms.AuthorForm(
                request.POST,
                instance=author,
            )
        else:
            author_form = submission_forms.AuthorForm(request.POST)
        if author_form.is_valid():
            author = author_form.save(commit=False)

            if not author.sequence:
                author.sequence = 1

            author.save()

            if not author_id:
                book.author.add(author)

            return redirect(
                reverse('swiftsubmit_authors', kwargs={'book_id': book.id})
            )

        if 'next_step' in request.POST:
            return redirect(
                reverse('swiftsubmit_stage', kwargs={'book_id': book.id})
            )

    template = "swiftsubmit/author.html"
    context = {'author_form': author_form, 'book': book}

    return render(request, template, context)


@is_press_editor
def editor(request, book_id, editor_id=None):

    book = get_object_or_404(core_models.Book, pk=book_id)

    if editor_id:
        if book.editor.filter(pk=editor_id).exists():
            editor = get_object_or_404(core_models.Editor, pk=editor_id)
            editor_form = submission_forms.EditorForm(instance=editor)
        else:
            return HttpResponseForbidden()
    else:
        editor = None
        editor_form = submission_forms.EditorForm()

    if request.method == 'POST':
        if editor:
            editor_form = submission_forms.EditorForm(
                request.POST,
                instance=editor,
            )
        else:
            editor_form = submission_forms.EditorForm(request.POST)
        if editor_form.is_valid():
            editor = editor_form.save(commit=False)

            if not editor.sequence:
                editor.sequence = 1

            editor.save()

            if not editor_id:
                book.editor.add(editor)

            return redirect(
                reverse('swiftsubmit_editors', kwargs={'book_id': book.id})
            )

    template = "swiftsubmit/editor.html"
    context = {'author_form': editor_form, 'book': book}

    return render(request, template, context)


def stage(request, book_id):

    book = get_object_or_404(core_models.Book, pk=book_id)
    form = forms.StageForm()

    if request.POST:
        form = forms.StageForm(request.POST)

        if form.is_valid():
            new_stage = form.save()
            book.stage = new_stage
            book.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Book has been submitted.'
            )
            return redirect(
                reverse('editor_submission', kwargs={'submission_id': book.id})
            )

    template = 'swiftsubmit/stage.html'
    context = {'book': book, 'form': form}

    return render(request, template, context)
