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


def send_acknowldgement_email(book, press_editors, sender):
    from_email = sender.email or get_setting('from_address', 'email')
    author_text = get_setting('author_submission_ack', 'email')
    editor_text = get_setting('editor_submission_ack', 'email')
    press_name = get_setting('press_name', 'general')

    principal_contact_name = get_setting('primary_contact_name', 'general')

    context = {
        'base_url': get_setting('base_url', 'general'),
        'submission': book,
        'press_name': press_name,
        'principal_contact_name': principal_contact_name,
    }

    email.send_email(
        get_setting(
            'submission_ack_subject',
            'email_subject',
            'Submission Acknowledgement'
        ), context,
        from_email,
        book.owner.email,
        author_text,
        book=book,
        kind='submission',
    )

    if len(press_editors) > 1:
        editor = press_editors[0]
        cc_eds = [ed.email for ed in press_editors if ed != press_editors[0]]
    else:
        editor = press_editors[0]
        cc_eds = None

    email.send_email(
        get_setting(
            'new_submission_subject',
            'email_subject',
            'New Submission'
        ),
        context,
        from_email,
        editor.email,
        editor_text,
        book=book,
        cc=cc_eds,
        kind='submission',
    )

    for editor in press_editors:
        notification = Task(
            book=book,
            assignee=editor,
            creator=press_editors[0],
            text='A new submission, {0}, has been made.'.format(book.title),
            workflow='review'
        )
        notification.save()


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
