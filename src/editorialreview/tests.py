from unittest import skip

import factory
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client

from editorialreview import models
from core import models as core_models
from review import models as review_models
from submission import models as submission_models


class UserFactory(factory.Factory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: 'user{}'.format(n))
    email = factory.LazyAttribute(
        lambda obj: '{}@example.com'.format(obj.username)
    )


class EditorialReviewerFactory(UserFactory):
    username = 'editorialreviewer'
    password = 'editorialreviewerpass'
    email = 'editorialreviewer@email.com'


class ProposalFormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = core_models.ProposalForm


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = core_models.Book


class ProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = submission_models.Proposal
    form = factory.SubFactory(ProposalFormFactory)


class BookEditorialReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EditorialReview
    content_object = factory.SubFactory(BookFactory)


class ProposalEditorialReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EditorialReview
    content_object = factory.SubFactory(ProposalFactory)


class EditorialReviewTests(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST='testing')
        self.editorialreviewer = EditorialReviewerFactory.create()
        self.editorialreviewer.set_password('reviewerpass')
        self.editorialreviewer.save()
        self.book = BookFactory.create()
        self.proposal = ProposalFactory.create()
        self.client.login(
            username=self.editorialreviewer.username,
            password='reviewerpass'  # Must be unhashed
        )

    def tearDown(self):
        pass

    def test_set_up(self):
        self.assertEqual(
            self.editorialreviewer.username,
            'editorialreviewer'
        )
        self.assertEqual(
            self.editorialreviewer.email,
            'editorialreviewer@email.com'
        )

    @skip(
        'Model factories need expanding. '
        'editorialreview.content_object.data is None.'
    )
    def test_ed_reviewer_download_proposal(self):
        self.editorialreview = ProposalEditorialReviewFactory.create(
            user=self.editorialreviewer
        )
        resp = self.client.get(
            reverse(
                'view_content_summary',
                kwargs={
                    'review_id': self.editorialreview.pk,
                }
            )
        )
        print resp.url
        self.assertEqual(resp.status_code, 200)
