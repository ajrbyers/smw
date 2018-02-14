import factory

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from editorialreview import models
from core import models as core_models


class UserFactory(factory.Factory):
    class Meta:
        model = User
    username = 'editorialreviewer'
    password = 'editorialreviewerpass'
    email = 'editorialreviewer@email.com'


class BookFactory(factory.Factory):
    class Meta:
        model = core_models.Book


class EditorialReviewTests(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST='testing')
        self.user = UserFactory.create()
        self.book = BookFactory.create()
        # login = self.client.login(
        #     email='editorialreviewer@email.com',
        #     password='editorialreviewerpass'
        # )
        # self.assertEqual(login, True)

    def tearDown(self):
        pass

    def test_set_up(self):
        self.assertEqual(self.user.username, 'editorialreviewer')
        self.assertEqual(self.user.email, 'editorialreviewer@email.com')



