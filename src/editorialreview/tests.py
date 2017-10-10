from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from core import models as core_models
import models


class EditorialReviewTests(TestCase):

    # Dummy DBs
    fixtures = [
        'settinggroups',
        'settings',
        'langs',
        'cc-licenses',
        'role',
        'test/test_auth_data',
        'test/test_core_data',
        'test/test_review_data',
        'test/test_editorialreview_data'
    ]

    def setUp(self):
        self.client = Client(HTTP_HOST="testing")
        self.user = User.objects.get(username="rua_editorialreviewer")
        self.user.save()
        self.book = core_models.Book.objects.get(pk=1)

        login = self.client.login(username=self.user.username, password="tester")
        self.assertEqual(login, True)

    def tearDown(self):
        pass

    ##############################################	Model Tests	 ##############################################

