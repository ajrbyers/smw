from django.contrib.auth.models import User
from django.db import models


def proposal_status():
    return (
        ('submission', 'Submission'),
        ('revisions_required', 'Revisions Required'),
        ('revisions_submitted', 'Revisions Submitted'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )


def book_type_choices():
    return (
        ('monograph', 'Monograph'),
        ('edited_volume', 'Edited Volume'),
    )


class Proposal(models.Model):

    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Book Title',
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    author = models.CharField(
        max_length=255,
        verbose_name='Submitting author/editor',
    )
    date_submitted = models.DateTimeField(
        auto_now_add=True,
    )
    form = models.ForeignKey(
        'core.ProposalForm'
    )
    data = models.TextField(
        blank=True,
        null=True,
    )
    date_review_started = models.DateTimeField(
        blank=True,
        null=True,
    )
    review_assignments = models.ManyToManyField(
        'ProposalReview',
        related_name='review',
        null=True,
        blank=True,
    )
    review_form = models.ForeignKey(
        'review.Form',
        null=True,
        blank=True,
    )
    requestor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="editor_requestor",
    )
    revision_due_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    date_accepted = models.DateTimeField(
        blank=True,
        null=True,
    )
    book_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=book_type_choices(),
        help_text="A monograph is a work authored, in its entirety, by one or "
                  "more authors. An edited volume has different authors "
                  "for each chapter."
    )
    book_editors = models.ManyToManyField(
        User,
        null=True,
        blank=True,
        related_name='proposal_book_editors',
    )
    contract = models.ForeignKey(
        'core.Contract',
        null=True,
        blank=True,
        related_name='contract_of_proposal',
    )
    current_version = models.IntegerField(
        default=1
    )
    status = models.CharField(
        max_length=20,
        choices=proposal_status(),
        default='submission',
    )

    def status_verbose(self):
        return dict(proposal_status())[self.status]

    def in_review(self):
        if ProposalReview.objects.filter(proposal=self).count() > 0:
            return True
        else:
            return False

    def reviews_completed(self):
        if ProposalReview.objects.filter(proposal=self, completed__isnull=True):
            return False
        else:
            return True


class HistoryProposal(models.Model):

    version = models.IntegerField(
        default=1
    )
    proposal = models.ForeignKey(
        Proposal,
        related_name='parent_proposal'
    )
    user_edited = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name='edited_by_user',
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name='parent_proposal_user',
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Book Title',
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    author = models.CharField(
        max_length=255,
        verbose_name='Submitting author/editor',
    )
    date_submitted = models.DateTimeField(
        auto_now_add=True,
    )
    form = models.ForeignKey(
        'core.ProposalForm',
        related_name='parent_proposal_Form',
    )
    data = models.TextField(
        blank=True,
        null=True,
    )
    date_review_started = models.DateTimeField(
        blank=True,
        null=True,
    )
    review_form = models.ForeignKey(
        'review.Form',
        null=True,
        blank=True,
    )
    requestor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="parent_proposal_Requestor",
    )
    revision_due_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    date_accepted = models.DateTimeField(
        blank=True,
        null=True,
    )
    date_edited = models.DateTimeField(
        blank=True,
        null=True,
    )
    book_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=book_type_choices(),
        help_text="A monograph is a work authored, in its entirety, by one or "
                  "more authors. An edited volume has different authors "
                  "for each chapter."
    )
    status = models.CharField(
        max_length=20,
        choices=proposal_status(),
        default='submission',
    )

    def status_verbose(self):
        return dict(proposal_status())[self.status]


class ProposalNote(models.Model):

    proposal = models.ForeignKey(
        Proposal,
    )
    user = models.ForeignKey(
        User,
    )
    date_submitted = models.DateTimeField(
        auto_now_add=True,
    )
    date_last_updated = models.DateTimeField(
        auto_now=True,
    )
    text = models.TextField(
        null=True,
        blank=True,
    )

    def truncated_content(self):
        content = str(self.text)
        if len(content) >= 22:
            content = content[:22] + '...'
        return content


class IncompleteProposal(models.Model):

    owner = models.ForeignKey(
        User,
        blank=True,
        null=True)
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Book Title')
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Submitting author/editor')
    form = models.ForeignKey(
        'core.ProposalForm',
        blank=True,
        null=True)
    data = models.TextField(
        blank=True,
        null=True)
    book_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=book_type_choices(),
        help_text="A monograph is a work authored, in its entirety, by one or "
                  "more authors. An edited volume has different authors for "
                  "each chapter."
    )
    status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=proposal_status(),
        default='submission',
    )

    def status_verbose(self):
        return dict(proposal_status())[self.status]


class SubmissionChecklistItem(models.Model):

    class Meta:
        ordering = ('sequence', 'text')

    slug = models.CharField(
        max_length=100,
    )
    text = models.CharField(
        max_length=500,
    )
    sequence = models.IntegerField(
        default=999,
    )
    required = models.BooleanField(
        default=True,
    )


def review_recommendation():
    return (
        ('accept', 'Accept'),
        ('reject', 'Reject'),
        ('revisions', 'Revisions Required')
    )


class ProposalReview(models.Model):

    class Meta:
        unique_together = ('proposal', 'user')

    proposal = models.ForeignKey(
        Proposal,
    )  # TODO: Remove: it is already linked to the book through the review round
    user = models.ForeignKey(
        User,
    )
    assigned = models.DateField(
        auto_now_add=True,
    )
    accepted = models.DateField(
        blank=True,
        null=True,
    )
    declined = models.DateField(
        blank=True,
        null=True,
    )
    due = models.DateField(
        blank=True,
        null=True,
    )
    completed = models.DateField(
        blank=True,
        null=True,
    )
    files = models.ManyToManyField(
        'core.File',
        blank=True,
        null=True,
    )
    results = models.ForeignKey(
        'review.FormResult',
        null=True,
        blank=True,
    )
    recommendation = models.CharField(
        max_length=10,
        choices=review_recommendation(),
        null=True,
        blank=True,
    )
    competing_interests = models.TextField(
        blank=True,
        null=True,
        help_text="If any of the authors or editors have any competing "
                  "interests please add them here. e.g.. 'This study was paid "
                  "for by corp xyz.'"
    )
    blind = models.NullBooleanField(
        default=False,
        blank=True,
        null=True,
    )
    requestor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="review_requestor",
    )
    review_form = models.ForeignKey(
        'review.Form',
        null=True,
        blank=True,
    )
    access_key = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    hide = models.BooleanField(
        default=False,
    )
    comments_from_editor = models.TextField(
        blank=True,
        null=True,
    )
    reopened = models.BooleanField(
        default=False
    ),
    withdrawn = models.BooleanField(
        default=False
    ),

    def __unicode__(self):
        return u'%s - %s %s' % (self.pk, self.proposal.title, self.user.username)

    def __repr__(self):
        return u'%s - %s %s' % (self.pk, self.proposal.title, self.user.username)
