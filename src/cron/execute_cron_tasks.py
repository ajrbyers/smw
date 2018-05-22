from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from core import models, email
from core.setting_util import get_setting
from revisions import models as revision_models


def remind_unaccepted_reviews(task):
    days = int(get_setting('remind_unaccepted_reviews', 'cron'))
    email_text = get_setting('unaccepted_reminder', 'email')

    dt = timezone.now()
    target_date = dt - timedelta(days=days)
    books = models.Book.objects.filter(stage__current_stage='review')

    for book in books:
        reviews = models.ReviewAssignment.objects.filter(
            book=book,
            review_round__round_number=book.get_latest_review_round(),
            unaccepted_reminder=False,
            accepted__isnull=True,
            declined__isnull=True,
            assigned=target_date.date,
        )
        for review in reviews:
            send_reminder_email(
                book, get_setting(
                    'review_request_reminder_subject',
                    'email_subject',
                    'Review Request Reminder'
                ),
                review,
                email_text,
            )
            # Lets make sure that we don't accidentally send this twice.
            review.unaccepted_reminder = True
            review.save()


def remind_accepted_reviews(task):
    days = int(get_setting('remind_accepted_reviews', 'cron'))
    email_text = get_setting('accepted_reminder', 'email')

    dt = timezone.now()
    target_date = dt + timedelta(days=days)
    books = models.Book.objects.filter(stage__current_stage='review')

    for book in books:
        reviews = models.ReviewAssignment.objects.filter(
            book=book,
            review_round__round_number=book.get_latest_review_round(),
            accepted_reminder=False,
            accepted__isnull=False,
            completed__isnull=True,
            declined__isnull=True,
            due=target_date.date,
        )
        for review in reviews:
            send_reminder_email(
                book,
                get_setting(
                    'review_request_reminder_subject',
                    'email_subject',
                    'Review Request Reminder'
                ),
                review,
                email_text,
            )
            # Lets make sure that we don't accidentally send this twice.
            review.accepted_reminder = True
            review.save()


def remind_overdue_reviews(task):
    days = int(get_setting('remind_overdue_reviews', 'cron'))
    email_text = get_setting('overdue_reminder', 'email')

    dt = timezone.now()
    target_date = dt - timedelta(days=days)
    books = models.Book.objects.filter(stage__current_stage='review')

    for book in books:
        reviews = models.ReviewAssignment.objects.filter(
            book=book,
            review_round__round_number=book.get_latest_review_round(),
            overdue_reminder=False,
            completed__isnull=True,
            declined__isnull=True,
            due=target_date.date
        )

        for review in reviews:
            send_reminder_email(
                book,
                get_setting(
                    'review_request_reminder_subject',
                    'email_subject',
                    'Review Request Reminder'
                ),
                review,
                email_text,
            )
            # Lets make sure that we don't accidentally send this twice.
            review.overdue_reminder = True
            review.save()


def reminder_overdue_revisions(task):
    days = int(get_setting('revisions_reminder', 'cron'))
    email_text = get_setting('revisions_reminder_email', 'email')

    dt = timezone.now()
    target_date = dt - timedelta(days=days)
    books = models.Book.objects.filter(
        Q(stage__current_stage='review') | Q(stage__current_stage='submission')
    )

    for book in books:
        revisions = revision_models.Revision.objects.filter(
            book=book,
            completed__isnull=True,
            overdue_reminder=False,
            due=target_date.date,
        )

        for review in revisions:
            review.user = review.book.owner
            send_reminder_email(
                book,
                get_setting(
                    'revision_request_reminder_subject',
                    'email_subject',
                    'Revision Request Reminder'
                ),
                review,
                email_text,
            )
            review.overdue_reminder = True
            review.save()


def reminder_notifications_not_emailed(task):
    from_email = get_setting('from_address', 'email')
    press_name = get_setting('press_name', 'general')
    email_text = get_setting('notification_reminder_email', 'email')

    editors = User.objects.filter(
        Q(profile__roles__slug='press-editor') |
        Q(profile__roles__slug='book-editor') |
        Q(profile__roles__slug='production-editor')
    )

    for editor in editors:
        tasks = models.Task.objects.filter(
            assignee=editor,
            emailed=False,
            completed__isnull=True,
        )
        task_list = ""

        for notification in tasks:
            task_list = task_list + '- ' + notification.text + "\n"
            notification.emailed = True
            notification.save()

        if task_list:
            context = {
                'user': editor,
                'notifications': task_list,
                'notification_count': tasks.count(),
                'press_name': press_name,
                'base_url': get_setting('base_url', 'general'),
            }
            email.send_email(
                get_setting(
                    'weekly_notification_reminder_subject',
                    'email_subject',
                    'Weekly Notification Reminder'
                ),
                context,
                from_email,
                editor.email,
                email_text
            )


def send_reminder_email(book, subject, review, email_text):
    from_email = get_setting('from_address', 'email')
    press_name = get_setting('press_name', 'general')

    context = {
        'book': book,
        'review': review,
        'press_name': press_name,
        'base_url': get_setting('base_url', 'general'),
    }
    email.send_email(
        subject,
        context,
        from_email,
        review.user.email,
        email_text,
        book=book,
        kind='reminder',
    )
