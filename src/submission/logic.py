from django.core.exceptions import PermissionDenied

from core import email
from core.models import Author, Editor, Task
from core.setting_util import get_setting


def copy_author_to_submission(user, book):
    author = Author(
        first_name=user.first_name,
        middle_name=user.profile.middle_name,
        last_name=user.last_name,
        salutation=user.profile.salutation,
        institution=user.profile.institution,
        department=user.profile.department,
        country=user.profile.country,
        author_email=user.email,
        biography=user.profile.biography,
        orcid=user.profile.orcid,
        twitter=user.profile.twitter,
        linkedin=user.profile.linkedin,
        facebook=user.profile.facebook,
    )

    author.save()
    book.author.add(author)

    return author


def copy_editor_to_submission(user, book):
    editor = Editor(
        first_name=user.first_name,
        middle_name=user.profile.middle_name,
        last_name=user.last_name,
        salutation=user.profile.salutation,
        institution=user.profile.institution,
        department=user.profile.department,
        country=user.profile.country,
        author_email=user.email,
        biography=user.profile.biography,
        orcid=user.profile.orcid,
        twitter=user.profile.twitter,
        linkedin=user.profile.linkedin,
        facebook=user.profile.facebook,
    )

    editor.save()
    book.editor.add(editor)

    return editor


def check_stage(book, check):
    if book.submission_stage >= check:
        pass
    elif book.submission_date:
        raise PermissionDenied()
    else:
        raise PermissionDenied()


def handle_book_labels(post, book, kind):
    for _file in book.files.all():
        if _file.kind == kind and post.get("%s" % _file.id, None):
            _file.label = post.get("%s" % _file.id)
            _file.save()


def handle_copyedit_author_labels(post, copyedit, kind):
    for _file in copyedit.author_files.all():
        if _file.kind == kind and post.get("%s" % _file.id, None):
            _file.label = post.get("%s" % _file.id)
            _file.save()
