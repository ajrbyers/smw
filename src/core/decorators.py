from django.contrib import messages
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404

from core import models
from editorialreview import models as editorialreview_models
from submission import models as submission_models


def is_author(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path())
            )

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        if 'author' in user_roles:
            return _function(request, *args, **kwargs)
        messages.add_message(
            request,
            messages.ERROR,
            'You need to have Author level permission to view this page.'
        )
        raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__
    return wrap


def is_press_editor(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path()))

        user_roles = [role.slug for role in request.user.profile.roles.all()]

        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        messages.add_message(
            request,
            messages.ERROR,
            (
                'You need to have Press Editor level '
                'permission to view this page.'
            )
        )
        raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_production_editor(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path()))

        user_roles = [role.slug for role in request.user.profile.roles.all()]

        if 'production-editor' in user_roles:
            return _function(request, *args, **kwargs)
        messages.add_message(
            request,
            messages.ERROR,
            (
                'You need to have Production Editor level '
                'permission to view this page.'
            )
        )
        raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_editor(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path()))

        user_roles = [role.slug for role in request.user.profile.roles.all()]

        if (
            'press-editor' in user_roles or
            'series-editor' in user_roles or
            'book-editor' in user_roles or
            'production-editor' in user_roles
        ):
            return _function(request, *args, **kwargs)
        messages.add_message(
            request,
            messages.ERROR,
            'You need to have Press Editor, Book Editor or Series '
            'Editor level permission to view this page.'
        )
        raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_book_editor(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path()))

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if (
                request.user in book.book_editors.all() or
                book.series in request.user.series_set.all()
            ):
                return _function(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        'You need to have Press Editor, Book Editor or Series '
                        'Editor level permission to view this page.')
                    )
                raise exceptions.PermissionDenied
        else:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    'You need to have Press Editor, Book Editor or Series '
                    'Editor level permission to view this page.')
                )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_book_editor_or_author(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path())
            )

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')
        elif kwargs.get('book_id'):
            submission_id = kwargs.get('book_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if (
                request.user in book.book_editors.all() or
                book.series in request.user.series_set.all() or
                book.owner == request.user
            ):
                return _function(request, *args, **kwargs)
            messages.add_message(
                request,
                messages.ERROR,
                (
                    'You need to have Press Editor, Book Editor or Series '
                    'Editor level permission to view this page.'
                )
            )
            raise exceptions.PermissionDenied
        messages.add_message(
            request,
            messages.ERROR,
            (
                'You need to have Press Editor, Book Editor or Series '
                'Editor level permission to view this page.'
            )
        )
        raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_reviewer(_function):
    def wrap(request, *args, **kwargs):
        one_click_no_login = models.Setting.objects.filter(
            name='one_click_review_url'
        )

        if one_click_no_login:
            if one_click_no_login[0].value == 'on':
                full_url = request.get_full_path()
                if 'access_key' in full_url:
                    if 'decision' in full_url:
                        access_key = full_url[full_url.rfind('key/') + 4:]
                        access_key = access_key.split('/', 1)[0]
                    elif 'complete' in full_url:
                        access_key = full_url[full_url.rfind('key/') + 4:]
                        access_key = access_key.split('/', 1)[0]
                    else:
                        access_key = full_url[full_url.rfind('key/') + 4:]
                        access_key = access_key[:access_key.rfind('/')]

                    review_assignments = models.ReviewAssignment.objects.filter(
                        access_key=access_key
                    )
                    proposal_review_assignments = (
                        submission_models.ProposalReview.objects.filter(
                            access_key=access_key
                        )
                    )

                    if review_assignments or proposal_review_assignments:
                        return _function(request, *args, **kwargs)

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path())
            )

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if request.user in [
                reviewer.user for reviewer in book.reviewassignment_set.all()
            ] or book.owner == request.user:
                return _function(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        'You need to have Press Editor, Book Editor or Series'
                        'Editor level permission to view this page.')
                    )
                raise exceptions.PermissionDenied
        elif not submission_id and 'reviewer' in user_roles:
            return _function(request, *args, **kwargs)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    'You need to have Press Editor, Book Editor or Series '
                    'Editor level permission to view this page.')
                )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_editor_or_ed_reviewer(_function):
    """Manage editorial reviewer permissions.

    Check if access key matches an existing editorial review, and otherwise
    handle editor permissions. Needs to be  improved so that ed reviewers can
    only see reviews for the submission they're reviewing.
    """
    def wrap(request, *args, **kwargs):
        full_url = request.get_full_path()
        if not request.user.is_authenticated():
            if 'access_key' in full_url:
                # Get access key from URI.
                access_key = full_url[full_url.rfind('access_key=') + 11:]
                review_assignment = get_object_or_404(
                    editorialreview_models.EditorialReview,
                    access_key=access_key
                )

                if review_assignment:
                    return _function(request, *args, **kwargs)

            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "{}?next={}".format(
                    reverse('login'),
                    request.get_full_path()
                )
            )

        else:

            if editorialreview_models.EditorialReview.objects.filter(
                user=request.user
            ):
                return _function(request, *args, **kwargs)

            user_roles = [r.slug for r in request.user.profile.roles.all()]

            if (
                    'press-editor' in user_roles or
                    'series-editor' in user_roles or
                    'production-editor' in user_roles or
                    'book-editor' in user_roles
            ):
                return _function(request, *args, **kwargs)

            review_assignment = get_object_or_404(
                editorialreview_models.EditorialReview,
                pk=kwargs.get('review_id')
            )
            submission = review_assignment.content_object  # Editor permissions.

            if review_assignment.content_type.model == 'book':
                if request.user in submission.all_editors():
                    return _function(request, *args, **kwargs)

            messages.add_message(
                request,
                messages.ERROR,
                'You cannot view this page as you are not '
                'an assigned editor or editorial reviewer.'
            )

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def has_reviewer_role(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path())
            )

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        if 'reviewer' in user_roles:
            return _function(request, *args, **kwargs)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'You need to have Reviewer level permission to view this page.'
            )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_indexer(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path())
            )

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if request.user in [
                reviewer.indexer for reviewer in book.indexassignment_set.all()
            ] or book.owner == request.user:
                return _function(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        'You need to have Press Editor, Book Editor or Series '
                        'Editor level permission to view this page.'
                    )
                )
                raise exceptions.PermissionDenied
        elif not submission_id and 'indexer' in user_roles:
            return _function(request, *args, **kwargs)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'You need to have Press Editor, Book Editor or Series Editor '
                'level permission to view this page.'
            )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_copyeditor(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path())
            )

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if request.user in [
                reviewer.copyeditor for reviewer
                in book.copyeditassignment_set.all()
            ] or book.owner == request.user:
                return _function(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        'You need to have Press Editor, Book Editor or Series '
                        'Editor level permission to view this page.'
                    )
                )
                raise exceptions.PermissionDenied
        elif not submission_id and 'copyeditor' in user_roles:
            return _function(request, *args, **kwargs)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'You need to have Press Editor, Book Editor or Series Editor '
                'level permission to view this page.'
            )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_typesetter(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(
                request,
                messages.ERROR,
                'You need to log in to view this page.'
            )
            return redirect(
                "%s?next=%s" % (reverse('login'), request.get_full_path()))

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if request.user in [
                reviewer.typesetter for reviewer in
                book.copyeditassignment_set.all()
            ] or book.owner == request.user:
                return _function(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'You need to have Press Editor, Book Editor or Series '
                    'Editor level permission to view this page.'
                )
                raise exceptions.PermissionDenied
        elif not submission_id and 'typesetter' in user_roles:
            return _function(request, *args, **kwargs)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'You need to have Press Editor, Book Editor or Series Editor '
                'level permission to view this page.'
            )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap


def is_onetasker(_function):
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated():
            messages.add_message(request, messages.ERROR,
                                 'You need to log in to view this page.')
            raise exceptions.PermissionDenied

        user_roles = [role.slug for role in request.user.profile.roles.all()]
        submission_id = False

        if kwargs.get('submission_id'):
            submission_id = kwargs.get('submission_id')

        # Check if the user is a press-editor, if not, check if they are they
        # are assigned as an editor to this book, or check if the user is the
        # series editor for this book.
        if 'press-editor' in user_roles:
            return _function(request, *args, **kwargs)
        elif submission_id:
            book = get_object_or_404(models.Book, pk=submission_id)
            if (
                request.user in book.onetaskers() or
                request.user in book.all_editors() or
                book.owner == request.user
            ):
                return _function(request, *args, **kwargs)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'You do not have permission to access this resource.'
                )
                raise exceptions.PermissionDenied
        elif (
            not submission_id and
            (set(user_roles) & {'copyeditor', 'typesetter', 'indexer'})
        ):
            return _function(request, *args, **kwargs)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    'You need to have Press Editor, Book Editor or Series '
                    'Editor level permission to view this page.'
                )
            )
            raise exceptions.PermissionDenied

    wrap.__doc__ = _function.__doc__
    wrap.__name__ = _function.__name__

    return wrap
