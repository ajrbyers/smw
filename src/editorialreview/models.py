from datetime import date
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


def review_recommendation():
    return (
        ('accept', 'Accept'),
        ('reject', 'Reject'),
        ('revisions', 'Revisions Required')
    )


class EditorialReview(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User)
    assigned = models.DateField(auto_now_add=True)
    due = models.DateField(blank=True, null=True)
    completed = models.DateField(blank=True, null=True)
    files = models.ManyToManyField('core.File', blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    access_key = models.CharField(max_length=200, null=True, blank=True)
    results = models.ForeignKey('review.FormResult', null=True, blank=True)
    recommendation = models.CharField(max_length=10,
                                      choices=review_recommendation(),
                                      null=True, blank=True)
    competing_interests = models.TextField(blank=True, null=True,
                                           help_text=mark_safe(
                                               "If any of the authors or editors have any competing interests "
                                               "please add them here. e.g.. 'This study was paid for by corp xyz.'."
                                               " <a href='/page/competing_interests/'>More info</a>"
                                           )
                                           )

    # Used to ensure that an email is not sent more than once.
    overdue_reminder = models.BooleanField(default=False)

    reopened = models.BooleanField(default=False)
    withdrawn = models.BooleanField(default=False)

    review_form = models.ForeignKey('review.Form', null=True, blank=True)

    def __str__(self):
        return '{0} - {1} ({2})'.format(self.content_object.title.encode('utf8'),
                                        self.user.profile.full_name().encode('utf8'),
                                        self.content_type)

    def is_overdue(self):
        return date.today() > self.due
