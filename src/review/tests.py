from django.test import TestCase
from django.utils import timezone
from django.http import HttpRequest
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve, reverse
from django.test import SimpleTestCase
from django.db.models import Q

from review import models
from review import views
from core import models as core_models

import json
from __builtin__ import any as string_any
import calendar
import tempfile
import time
import datetime
# Create your tests here.

class ReviewTests(TestCase):

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
    ]

    def setUp(self):
        self.client = Client(HTTP_HOST="testing")
        self.user = User.objects.get(username="rua_reviewer")
        self.user.save()
        self.book = core_models.Book.objects.get(pk=1)

        login = self.client.login(username="rua_reviewer", password="tester")
        self.assertEqual(login, True)

    def tearDown(self):
        pass

    def test_set_up(self):
        """
        testing set up
        """
        self.assertEqual(self.user.username == "rua_reviewer", True)
        self.assertEqual(self.user.email == "fake_reviewer@fakeaddress.com", True)
        self.assertEqual(self.user.first_name == "rua_reviewer_first_name", True)
        self.assertEqual(self.user.last_name == "rua_reviewer_last_name", True)
        self.assertEqual(self.user.profile.institution == "rua_testing", True)
        self.assertEqual(self.user.profile.country == "GB", True)

    def test_reviewer_access(self):
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_not_reviewer_access(self):
        login = self.client.login(username="rua_author", password="tester")
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, True)

    def test_reviewer_dashboard(self):

        pending_tasks = core_models.ReviewAssignment.objects.filter(user=self.user, completed__isnull=True, declined__isnull=True).select_related('book')
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual(len(pending_tasks) == 1, True)
        self.assertEqual("Review requested for" in content, True)
        self.assertEqual("rua_title" in content, True)
        self.assertEqual("View Task" in content, True)
        self.assertEqual("You can accept or reject this task" in content, True)

        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        self.assignment.accepted = timezone.now()
        self.assignment.save()

        pending_tasks = core_models.ReviewAssignment.objects.filter(user=self.user, completed__isnull=True, declined__isnull=True).select_related('book')
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual(len(pending_tasks) == 1, True)
        self.assertEqual("Review requested for" in content, True)
        self.assertEqual("rua_title" in content, True)
        self.assertEqual("View Task" in content, True)

        month = time.strftime("%m")
        day = time.strftime("%d")
        year = time.strftime("%Y")

        message = "You accepted on %s-%s-%s" % (year, month, day)
        print message
        self.assertEqual(message in content, True)

        self.assignment.completed = timezone.now()
        self.assignment.save()
        completed_tasks = core_models.ReviewAssignment.objects.filter(user=self.user, completed__isnull=False).select_related('book')
        self.assertEqual(len(completed_tasks) == 1, True)
        pending_tasks = core_models.ReviewAssignment.objects.filter(user=self.user, completed__isnull=True, declined__isnull=True).select_related('book')
        self.assertEqual(len(pending_tasks) == 0, True)
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Review requested for" in content, False)
        self.assertEqual("1 COMPLETED TASK" in content, True)
        message = "Accepted on <b>%s-%s-%s</b>" % (year, month, day)
        self.assertEqual(message in content, True)
        message = "Completed on <b>%s-%s-%s</b>" % (year, month, day)
        self.assertEqual(message in content, True)

        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        self.assignment.accepted = None
        self.assignment.completed = None
        self.assignment.declined = timezone.now()
        self.assignment.save()
        pending_tasks = core_models.ReviewAssignment.objects.filter(user=self.user, completed__isnull=True, declined__isnull=True).select_related('book')
        completed_tasks = core_models.ReviewAssignment.objects.filter(user=self.user, completed__isnull=False).select_related('book')
        self.assertEqual(len(completed_tasks) == 0, True)
        self.assertEqual(len(pending_tasks) == 0, True)
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("0 COMPLETED TASKS" in content, True)

    def test_reviewer_decision(self):
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        resp = self.client.get(reverse('reviewer_decision_without', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("You can accept or reject this task" in content, True)
        self.assertEqual("I Accept" in content, True)
        self.assertEqual("I Decline" in content, True)
        resp = self.client.get(reverse('reviewer_decision_with', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1, 'decision': 'decline'}))
        content = resp.content

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/dashboard/")
        self.assignment.declined = None
        self.assignment.save()
        resp = self.client.get(reverse('reviewer_decision_with', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1, 'decision': 'accept'}))
        content = resp.content

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/review-round/1/")

    def test_reviewer_decision_accept(self):
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        resp = self.client.post(reverse('reviewer_decision_without', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1}), {'accept': 'I Accept'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/%s/%s/review-round/1/" % (self.assignment.review_type, 1))

    def test_reviewer_decision_decline(self):
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        resp = self.client.post(reverse('reviewer_decision_without', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1}), {'decline': 'I Decline'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/dashboard/")

    def test_reviewer_assignment(self):
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        self.assignment.save()
        resp = self.client.get(reverse('review_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/assignment/1/decision/")

        self.assignment.accepted = timezone.now()
        self.assignment.save()
        resp = self.client.get(reverse('review_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        month = time.strftime("%m")
        day = time.strftime("%d")
        year = time.strftime("%Y")
        message = "You accepted on %s-%s-%s" % (year, month, day)
        self.assertEqual(message in content, True)
        resp = self.client.get(reverse('review_complete', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/review-round/1/")
        resp = self.client.post(reverse('review_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}), {'rua_name': 'example', 'recommendation': 'accept', 'competing_interests': 'nothing'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/review-round/1/complete/")

        resp = self.client.get(reverse('review_complete', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assignment.reopened = True
        self.assignment.save()
        form_results = models.FormResult(form=self.book.review_form, data="")
        form_results.data = '{"rua_name": ["cxxccxc", "text"]}'
        form_results.save()
        self.assignment.results = form_results
        self.assignment.save()
        self.assertEqual(self.assignment.reopened, True)
        resp = self.client.get(reverse('review_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('review_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_round': 1}), {'rua_name': 'example', 'recommendation': 'accept', 'competing_interests': 'nothing'})
        self.assertEqual(resp.status_code, 302)
        print resp.content
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        self.assertEqual(self.assignment.reopened, False)

    def test_access_key(self):
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        self.assignment.access_key = "enter"
        self.assignment.save()
        resp = self.client.get(reverse('reviewer_decision_without', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1}))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(reverse('reviewer_decision_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1, 'access_key': "enter"}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("You can accept or reject this task" in content, True)
        self.assertEqual("I Accept" in content, True)
        self.assertEqual("I Decline" in content, True)

        resp = self.client.post(reverse('reviewer_decision_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1, 'access_key': "enter"}), {'accept': 'I Accept'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/%s/%s/review-round/1/access_key/%s/" % (self.assignment.review_type, 1, "enter"))
        resp = self.client.get(reverse('review_complete_with_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'access_key': "enter", 'review_round': 1}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/review-round/1/access_key/enter/")
        self.assignment.accepted = None
        self.assignment.save()
        resp = self.client.post(reverse('reviewer_decision_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1, 'access_key': "enter"}), {'decline': 'I Decline'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/dashboard/")
        self.assignment.declined = None
        self.assignment.accepted = timezone.now()
        self.assignment.save()
        resp = self.client.post(reverse('review_with_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'access_key': "enter", 'review_round': 1}), {'rua_name': 'example', 'recommendation': 'accept', 'competing_interests': 'nothing'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/review-round/1/access_key/enter/complete/")
        resp = self.client.get(reverse('review_complete_with_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'access_key': "enter", 'review_round': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_files_reviewer(self):
        self.assignment = core_models.ReviewAssignment.objects.get(pk=1)
        self.assignment.access_key = "enter"
        self.assignment.save()
        resp = self.client.post(reverse('reviewer_decision_without_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'review_assignment_id': 1, 'access_key': "enter"}), {'accept': 'I Accept'})
        path = views.create_review_form(self.book, self.book.review_form)
        self.assertEqual("/files/forms/" in path, True)
        self.assertEqual(".docx" in path, True)
        review_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(reverse('review_with_access_key', kwargs={'review_type': self.assignment.review_type, 'submission_id': 1, 'access_key': "enter", 'review_round': 1}), {'rua_name': 'example', 'recommendation': 'accept', 'competing_interests': 'nothing', 'review_file_upload': review_file})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/external/1/review-round/1/access_key/enter/complete/")
