#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.contrib.auth.models import User
from django.core import management
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.test.utils import setup_test_environment
from django.utils import timezone

import factory

from core import models
from submission import models as submission_models
import tempfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

    username = 'test_user'


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'core.Book'
        django_get_or_create = ('title',)

    title = 'Testing for Dummies'


class SeriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'core.Series'
        django_get_or_create = ('name',)

    name = 'A Series of Tests'


class CoreTests(TestCase):
    # Dummy DBs
    fixtures = [
        'settinggroups',
        'settings/master',
        'langs',
        'cc-licenses',
        'role',
        'test/test_auth_data',
        'test/test_unicode_core_data',
        'test/test_review_data',
        'test/test_proposal_form',
        'test/test_submission_proposal',
    ]

    # Helper Functions
    @staticmethod
    def getmessage(response):
        """Helper method to return first message from response """
        for c in response.context:
            message = [m for m in c.get('messages')][0]
            if message:
                return message

    @staticmethod
    def get_specific_message(response, number):
        """Helper method to return first message from response """
        for c in response.context:
            message = [m for m in c.get('messages')][number]
            if message:
                return message

    def setUp(self):
        self.client = Client(HTTP_HOST="testing")
        self.user = User.objects.get(pk=1)
        setup_test_environment()
        login = self.client.login(username=self.user.username, password="root")
        self.assertEqual(login, True)

        self.assertEqual(self.user.username == "rua_user", True)
        self.assertEqual(self.user.email == "fake_user@fakeaddress.com", True)
        self.assertEqual(self.user.first_name == "rua_user_first_name", True)
        self.assertEqual(self.user.last_name == "rua_user_last_name", True)
        self.assertEqual(self.user.profile.institution == "rua_testing", True)
        self.assertEqual(self.user.profile.country == "GB", True)

    def tearDown(self):
        pass

    def all_x_exist(self, model, key, expected_val_list):
        for expected_val in expected_val_list:
            try:
                model.objects.get(**{key: expected_val})
            except model.DoesNotExist:
                self.fail(
                    "No {model_name} with a {key} of {value} found".format(
                        model_name=model.__name__,
                        key=key,
                        value=expected_val,
                    )
                )

    # ## Fixture Tests ##

    def test_roles_fixture(self):
        """
        testing roles fixture
        """
        expected_roles = ["Reader",
                          "Author",
                          "Copyeditor",
                          "Reviewer",
                          "Press Editor",
                          "Production Editor",
                          "Book Editor",
                          "Series Editor",
                          "Indexer",
                          "Typesetter"]
        self.all_x_exist(models.Role, 'name', expected_roles)

    def test_settings_fixture(self):
        """
        testing settings fixture
        """
        settings = ["accronym",
                    "editorial_assignment_feature",
                    "proposal_contract_author_sign_off",
                    "default_review_type",
                    "review_type_selection",
                    "submit_proposals",
                    "additional_files_guidelines",
                    "base_url",
                    "ci_required",
                    "city",
                    "copyedit_author_instructions",
                    "copyedit_instructions",
                    "description",
                    "direct_submissions",
                    "footer",
                    "index_instructions",
                    "instructions_for_task_copyedit",
                    "instructions_for_task_index",
                    "instructions_for_task_proposal",
                    "instructions_for_task_review",
                    "instructions_for_task_typeset",
                    "manuscript_guidelines",
                    "oai_identifier",
                    "press_name",
                    "preview_review_files",
                    "primary_contact_email",
                    "primary_contact_name",
                    "proposal_form",
                    "publishing_committee",
                    "registration_message",
                    "submission_checklist_help",
                    "submission_guidelines",
                    "suggested_reviewers",
                    "suggested_reviewers_guide",
                    "typeset_author_instructions",
                    "typeset_instructions",
                    "competing_interests",
                    "terms-conditions",
                    "accepted_reminder",
                    "author_copyedit_request",
                    "author_submission_ack",
                    "author_typeset_request",
                    "book_editor_ack",
                    "contract_author_sign_off",
                    "copyedit_request",
                    "decision_ack",
                    "editor_submission_ack",
                    "editorial_decision_ack",
                    "external_review_request",
                    "from_address",
                    "index_request",
                    "new_user_email",
                    "new_user_owner_email",
                    "notification_reminder_email",
                    "overdue_reminder",
                    "production_editor_ack",
                    "proposal_accept",
                    "proposal_decline",
                    "proposal_request_revisions",
                    "proposal_review_request",
                    "proposal_revision_submit_ack",
                    "proposal_submission_ack",
                    "proposal_update_ack",
                    "request_revisions",
                    "reset_password",
                    "review_due_ack",
                    "review_request",
                    "revisions_reminder_email",
                    "task_decline",
                    "typeset_request",
                    "typesetter_typeset_request",
                    "unaccepted_reminder",
                    "brand_header",
                    "favicon",
                    "notification_reminder",
                    "remind_accepted_reviews",
                    "remind_overdue_reviews",
                    "remind_unaccepted_reviews",
                    "revisions_reminder"]
        self.all_x_exist(models.Setting, 'name', settings)

    def test_setting_groups_fixture(self):
        """
        testing setting groups fixture
        """
        settings_groups = ["general", "page", "email", "look", "cron"]
        self.all_x_exist(models.SettingGroup, 'name', settings_groups)

    def test_cc_licenses_fixture(self):
        """
        testing cc licenses fixture
        """
        license_codes = ["cc-4-by", "cc-4-by-sa", "cc-4-by-nd", "cc-4-by-nc",
                         "cc-4-by-nc-nd", "cc-4-by-nd-sa"]
        self.all_x_exist(models.License, 'code', license_codes)

    def test_langs_fixture(self):
        """
        testing langs fixture
        """
        langs = ["abk", "afr", "afa", "amh", "anp", "apa", "ara", "hye", "asm",
                 "ast", "aus", "aze", "ban", "bat", "bas", "bak", "eus", "bel",
                 "ben", "ber", "bos", "bre", "bul", "mya", "cat", "cel", "cai",
                 "che", "chr", "zho", "cor", "cos", "hrv", "ces", "dak", "dan",
                 "dum", "nld", "eng", "est", "fao", "fij", "fil", "fin", "fiu",
                 "fra", "gla", "car", "glg", "lug", "gay", "gba", "gez", "kat",
                 "deu", "gmh", "goh", "gem", "gil", "hat", "haw", "heb", "hin",
                 "hun", "isl", "ind", "gle", "ita", "jpn", "tlh", "kon", "kor",
                 "kur", "kru", "lat", "lav", "lit", "nds", "lus", "ltz", "mkd",
                 "mlg", "msa", "mal", "mlt", "mni", "mri", "myn", "moh", "mol",
                 "mon", "new", "nep", "non", "nai", "nor", "nno", "pag", "pan",
                 "paa", "fas", "phi", "pol", "por", "ron", "rom", "rus", "smo",
                 "sco", "srp", "iii", "scn", "sla", "slk", "slv", "sog", "som",
                 "son", "wen", "spa", "zgh", "suk", "sun", "swa", "swe", "gsw",
                 "syr", "tha", "tog", "ton", "tsi", "tso", "tsn", "tum", "tur",
                 "ukr", "urd", "uzb", "vai", "ven", "vie", "cym", "yap", "yid",
                 "zap", "zha", "zul"]
        self.all_x_exist(models.Language, 'code', langs)

    # ## Model Tests ##

    def test_author_model(self):
        """
        test author model
        """
        self.author = models.Author.objects.get(pk=1)
        self.author.save()
        # model functions
        fullname = "%s %s" % ("rua_author_first_name", "rua_author_last_name")
        unicode_text = u'%s - %s %s' % (
        str(1), "rua_author_first_name", "rua_author_last_name")
        self.assertEqual(self.author.__repr__() == unicode_text, True)
        self.assertEqual(self.author.__unicode__() == unicode_text, True)
        self.assertEqual(self.author.full_name() == fullname, True)
        self.assertEqual(self.author.first_name == "rua_author_first_name",
                         True)
        self.assertEqual(self.author.last_name == "rua_author_last_name", True)
        self.assertEqual(self.author.institution == "rua_testing", True)
        self.assertEqual(self.author.country == "GB", True)
        self.assertEqual(self.author.author_email == "fake@fakeaddress.com",
                         True)
        self.assertEqual(self.author.full_name() == fullname, True)

        # alter field
        self.author.first_name = "rua_changed_first_name"
        self.author.save()

        self.assertEqual(self.author.first_name == "rua_changed_first_name",
                         True)
        # check number of created objects
        self.assertEqual(len(models.Author.objects.all()) == 1, True)

    def test_user_roles(self):
        user = models.User.objects.get(username="rua_user")
        roles = ["Reader", "Author", "Copyeditor", "Reviewer", "Press Editor",
                 "Book Editor", "Series Editor", "Indexer", "Typesetter"]
        for role in roles:
            self.assertEqual(user.profile.roles.filter(name=role).exists(),
                             True)

        user = models.User.objects.get(username="rua_reviewer")
        roles = ["Reviewer"]
        for role in roles:
            self.assertEqual(user.profile.roles.filter(name=role).exists(),
                             True)

        user = models.User.objects.get(username="rua_author")
        roles = ["Author"]
        for role in roles:
            self.assertEqual(user.profile.roles.filter(name=role).exists(),
                             True)

        user = models.User.objects.get(username="rua_editor")
        roles = ["Press Editor", "Book Editor", "Series Editor"]
        for role in roles:
            self.assertEqual(user.profile.roles.filter(name=role).exists(),
                             True)

        user = models.User.objects.get(username="rua_onetasker")
        roles = ["Copyeditor", "Indexer", "Typesetter"]
        for role in roles:
            self.assertEqual(user.profile.roles.filter(name=role).exists(),
                             True)

    def test_book_model(self):
        """
        test book model
        """
        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        self.author = models.Author.objects.get(pk=1)
        self.author.save()

        self.assertEqual(self.book.prefix == "rua_prefix", True)
        self.assertEqual(self.book.title == "rua_title", True)
        self.assertEqual(self.book.slug == "rua_title", True)
        self.assertEqual(self.book.subtitle == "rua_subtitle", True)
        self.assertEqual(self.book.description == "rua description", True)
        self.assertEqual(self.book.cover_letter == "cover letter", True)
        self.assertEqual(
            self.book.reviewer_suggestions == "reviewer suggestion", True)
        self.assertEqual(self.book.competing_interests == "competing interest",
                         True)
        self.assertEqual(self.book.book_type == "monograph", True)
        self.assertEqual(self.book.author.filter(pk=1).exists(), True)
        self.assertEqual(self.book.subject.filter(pk=1).exists(), True)
        self.assertEqual(self.book.keywords.filter(pk=1).exists(), True)
        self.assertEqual(self.book.press_editors.filter(pk=2).exists(), True)
        self.assertEqual(self.book.license == models.License.objects.get(pk=4),
                         True)
        self.assertEqual(self.book.owner == models.User.objects.get(pk=3), True)
        self.assertEqual(self.book.languages.filter(pk=124).exists(), True)

        # check that it exists in the database

        self.assertEqual(len(models.Book.objects.all()) == 1, True)

    # ## Dashboards ##

    def test_editor_access(self):
        self.client.login(username="rua_editor", password="tester")
        resp = self.client.get(reverse('editor_dashboard'))

        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_not_editor_access(self):
        self.client.login(username="rua_reviewer", password="tester")
        resp = self.client.get(reverse('editor_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, True)

    def test_editor_redirect(self):
        self.client.login(username="rua_editor", password="tester")
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, "http://testing/editor/dashboard/",
                             status_code=302, target_status_code=200, host=None,
                             msg_prefix='', fetch_redirect_response=True)

    def test_author_access(self):
        self.client.login(username="rua_author", password="tester")
        resp = self.client.get(reverse('author_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_not_author_access(self):
        self.client.login(username="rua_reviewer", password="tester")
        resp = self.client.get(reverse('author_dashboard'))
        content = resp.content
        self.user.last_login = timezone.now()
        self.user.save()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, True)

    def test_author_redirect(self):
        self.client.login(username="rua_author", password="tester")
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, "http://testing/author/dashboard/",
                             status_code=302, target_status_code=200, host=None,
                             msg_prefix='', fetch_redirect_response=True)

    def test_onetasker_access(self):
        self.client.login(username="rua_onetasker", password="tester")
        resp = self.client.get(reverse('onetasker_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_not_onetasker_access(self):
        self.client.login(username="rua_reviewer", password="tester")
        resp = self.client.get(reverse('onetasker_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, True)

    def test_onetasker_redirect(self):
        self.client.login(username="rua_onetasker", password="tester")
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, "http://testing/tasks/", status_code=302,
                             target_status_code=200, host=None, msg_prefix='',
                             fetch_redirect_response=True)

    def test_reviewer_access(self):
        self.client.login(username="rua_reviewer", password="tester")
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_not_reviewer_access(self):
        self.client.login(username="rua_author", password="tester")
        resp = self.client.get(reverse('reviewer_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, True)

    def test_reviewer_redirect(self):
        self.client.login(username="rua_reviewer", password="tester")
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, "http://testing/review/dashboard/",
                             status_code=302, target_status_code=200, host=None,
                             msg_prefix='', fetch_redirect_response=True)

    def test_view_profile(self):
        resp = self.client.get(reverse('view_profile'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("500" in content, False)

    def test_logout(self):
        resp = self.client.get(reverse('logout'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/")

    def test_login(self):
        resp = self.client.get(reverse('logout'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/")

        resp = self.client.post(reverse('login'),
                                {'user_name': 'rua_user', 'user_pass': "root"})
        self.assertEqual(resp['Location'], "http://testing/dashboard/")
        resp = self.client.get(reverse('logout'))

    def test_login_invalid(self):
        resp = self.client.get(reverse('logout'))
        resp = self.client.post(
            reverse('login'),
            {'user_name': 'unknown',
             'user_pass': "unknown"}
        )
        message = self.get_specific_message(resp, 1)
        self.assertEqual(str(message), 'Account not found with those details.')

    def test_login_not_active(self):
        resp = self.client.get(reverse('logout'))
        resp = self.client.get(reverse('register'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(
            reverse('register'),
            {'first_name': 'new',
             'last_name': 'last',
             'username': 'user1',
             'email': 'fake@faked.com',
             'password1': 'password1',
             'password2': 'password1',
             'institution': 'Institute of Testable Hypotheses',
             'country': 'GB'
             }
        )
        user = User.objects.get(username="user1")
        roles = models.Role.objects.filter(name__icontains="Editor")
        for role in roles:
            user.profile.roles.add(role)
        user.profile.save()
        user.save()
        resp = self.client.post(
            reverse('login'),
            {'user_name': 'user1',
             'user_pass': "password1"}
        )
        message = self.get_specific_message(resp, 0)
        self.assertEqual(
            str(message),
            'An email has been sent with a user activation link. øö'
        )

    def test_activate_user(self):
        resp = self.client.post(reverse('register'), {
            'first_name': 'new',
            'last_name': 'last',
            'username': 'user1',
            'email': 'fake@faked.com',
            'password1': 'password1',
            'password2': "password1",
            'institution': 'Intitute of Testable Hypotheses',
            'country': 'GB',
        })
        user = User.objects.get(username="user1")
        roles = models.Role.objects.filter(name__icontains="Editor")
        for role in roles:
            user.profile.roles.add(role)
        user.profile.activation_code = 'activate'
        user.profile.save()
        user.save()
        resp = self.client.post(
            reverse('activate', kwargs={'code': 'activate'}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/login/")

    def test_index(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/login/")

    def test_contact(self):
        resp = self.client.get(reverse('contact'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Get in touch" in content, True)
        self.assertEqual("Reason" in content, True)
        self.assertEqual("Your email address" in content, True)
        self.assertEqual("Your name" in content, True)
        self.assertEqual("Your message" in content, True)

    def test_user_submission(self):
        self.client.login(username="rua_author", password="tester")
        resp = self.client.get(
            reverse('user_submission', kwargs={'submission_id': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("rua_title" in content, True)
        self.assertEqual("Submission Progress" in content, True)
        self.assertEqual("Summary" in content, True)
        self.assertEqual("Files" in content, True)
        self.assertEqual("Authors" in content, True)

    def test_overview(self):
        resp = self.client.get(reverse('overview'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("New Submissions" in content, True)
        self.assertEqual("In Review" in content, True)
        self.assertEqual("In Editing" in content, True)
        self.assertEqual("In Production" in content, True)

        resp = self.client.get(reverse('overview_inprogress'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        self.assertEqual("Submissions In Progress" in content, True)

        resp = self.client.get(reverse('proposal_overview'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Proposals" in content, True)
        self.assertEqual("Accepted Proposals" in content, True)
        self.assertEqual("Declined Proposals" in content, True)

    def test_proposals(self):
        proposal = submission_models.Proposal.objects.get(pk=1)
        self.client.login(username="rua_editor", password="tester")
        resp = self.client.get(reverse('proposals'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Book Proposals" in content, True)
        self.assertEqual(proposal.title in content, True)
        view_button = "/proposals/%s/" % proposal.id
        self.assertEqual(view_button in content, True)

        resp = self.client.get(
            reverse('view_proposal', kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        page_title = "Book Proposal : {title}".format(
            title=proposal.title,
        )
        self.assertTrue(page_title in content)

        proposal_reviews = submission_models.ProposalReview.objects.all()
        self.assertEqual(0, len(proposal_reviews))
        resp = self.client.get(
            reverse('view_proposal', kwargs={'proposal_id': proposal.id}),
            {'download': 'docx'})

        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('start_proposal_review',
                                       kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(reverse('start_proposal_review',
                                        kwargs={'proposal_id': proposal.id}),
                                {'due_date': '2015-11-11', 'review_form': 1,
                                 'committee': 2, 'reviewer': 1,
                                 'email_text': 'hi'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/proposals/1/")
        proposal_reviews = submission_models.ProposalReview.objects.all()
        self.assertEqual(len(proposal_reviews) == 0, False)

        resp = self.client.get(reverse('withdraw_proposal_review',
                                       kwargs={'proposal_id': proposal.id,
                                               'review_id': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        proposal_review = submission_models.ProposalReview.objects.get(pk=1)

        self.assertEqual(proposal_review.withdrawn, True)

        resp = self.client.get(reverse('withdraw_proposal_review',
                                       kwargs={'proposal_id': proposal.id,
                                               'review_id': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        proposal_review = submission_models.ProposalReview.objects.get(pk=1)

        self.assertEqual(proposal_review.withdrawn, False)

        resp = self.client.get(
            reverse('accept_proposal', kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        proposal_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(
            reverse('accept_proposal', kwargs={'proposal_id': proposal.id}),
            {'proposal-type': 'monograph', 'accept-email': 'Dear user',
             'attachment-file': proposal_file})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/proposals/")
        proposal = submission_models.Proposal.objects.get(pk=1)
        self.assertEqual(proposal.status, 'accepted')
        proposal.status = 'submission'
        proposal.save()
        resp = self.client.get(
            reverse('decline_proposal', kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(
            reverse('decline_proposal', kwargs={'proposal_id': proposal.id}),
            {'decline-email': 'Dear user'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/proposals/")
        proposal = submission_models.Proposal.objects.get(pk=1)
        self.assertEqual(proposal.status, 'declined')
        proposal.status = 'submission'
        proposal.save()
        resp = self.client.get(reverse('request_proposal_revisions',
                                       kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(reverse('request_proposal_revisions',
                                        kwargs={'proposal_id': proposal.id}),
                                {'revisions-email': 'Dear user',
                                 'due_date': '2015-11-11'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/proposals/")
        proposal = submission_models.Proposal.objects.get(pk=1)
        self.assertEqual(proposal.status, 'revisions_required')
        proposal.status = 'submission'
        proposal.save()
        resp = self.client.get(reverse('add_proposal_reviewers',
                                       kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(reverse('add_proposal_reviewers',
                                        kwargs={'proposal_id': proposal.id}),
                                {'due_date': '2015-11-11', 'committee': ['2'],
                                 'email_text': 'hi'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/proposals/1/")

    def test_proposals_exists_in_committee(self):
        proposal = submission_models.Proposal.objects.get(pk=1)
        self.client.login(username="rua_editor", password="tester")
        proposal_reviews = submission_models.ProposalReview.objects.all()
        self.assertEqual(0, len(proposal_reviews))
        resp = self.client.get(reverse('start_proposal_review',
                                       kwargs={'proposal_id': proposal.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(reverse('start_proposal_review',
                                        kwargs={'proposal_id': proposal.id}),
                                {'due_date': '2015-11-11', 'review_form': 1,
                                 'committee': 2, 'reviewer': 4,
                                 'email_text': 'hi'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/proposals/1/")
        proposal_reviews = submission_models.ProposalReview.objects.all()

    def test_oai(self):

        resp = self.client.get(reverse('oai'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_ajax_email_calls(self):

        self.assertEqual(len(models.Book.objects.all()) == 1, True)
        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        self.author = models.Author.objects.get(pk=1)
        self.author.save()

        resp = self.client.get(
            reverse('get_authors', kwargs={'submission_id': self.book.id}),
            {'term': 'rua', }, content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(resp.content)
        self.assertEqual(self.author.author_email == json_data[0]["value"],
                         True)
        resp = self.client.get(
            reverse('get_editors', kwargs={'submission_id': self.book.id}),
            {'term': 'rua', }, content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(resp.content)
        editors = self.book.press_editors.all()
        self.assertEqual(editors[0].email == json_data[0]["value"], True)
        resp = self.client.get(
            reverse('get_onetaskers', kwargs={'submission_id': self.book.id}),
            {'term': 'rua', }, content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(resp.content)
        onetasker = User.objects.get(pk=5)
        self.assertEqual(onetasker.email == json_data[0]["value"], True)
        resp = self.client.get(
            reverse('get_all', kwargs={'submission_id': self.book.id}),
            {'term': 'rua', }, content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(resp.content)
        self.assertEqual(len(json_data) == 3, True)
        resp = self.client.get(
            reverse('get_all', kwargs={'submission_id': self.book.id}),
            {'term': 'none_term', }, content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(resp.content)
        self.assertEqual(len(json_data) == 0, True)

    def test_unauth_reset(self):
        resp = self.client.get(reverse('unauth_reset'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(reverse('unauth_reset'),
                                {'username': 'rua_author'})
        self.assertEqual(resp.status_code, 200)
        profile = models.Profile.objects.get(user__username='rua_author')

        resp = self.client.get(
            reverse('unauth_reset_code', kwargs={'uuid': profile.reset_code}))
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(reverse('unauth_reset_password',
                                       kwargs={'uuid': profile.reset_code}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(reverse('unauth_reset_password',
                                        kwargs={'uuid': profile.reset_code}),
                                {'password_1': 'testing12',
                                 'password_2': 'testing12'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/login/")

    def test_switch_account(self):
        resp = self.client.get(reverse('switch-account'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('switch-account-user', kwargs={'account_id': 4}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/dashboard/")
        resp = self.client.get(reverse('user_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/review/dashboard/")

    def test_page(self):
        resp = self.client.get(
            reverse('page', kwargs={'page_name': 'competing_interests'}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Competing Interests" in content, True)

    def test_log(self):
        resp = self.client.get(reverse('view_log', kwargs={'submission_id': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    def test_unassigned_proposal(self):
        resp = self.client.get(reverse('proposal_assign'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        proposals = submission_models.Proposal.objects.filter(
            owner__isnull=True)
        self.assertEqual(proposals.count(), 0)
        resp = self.client.post(
            reverse('proposal_assign'),
            {"book_submit": "True",
             "title": "rua_proposal_title",
             "subtitle": "rua_proposal_subtitle",
             "author": "rua_user", "rua_element": "example",
             "rua_element_2": "example"}
        )
        proposals = submission_models.Proposal.objects.filter(
            owner__isnull=True)
        self.assertEqual(proposals.count(), 1)
        proposal = proposals[0]
        resp = self.client.get(reverse('proposal_assign_edit',
                                       kwargs={'proposal_id': proposal.pk}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(
            reverse('proposal_assign_edit',
                    kwargs={'proposal_id': proposal.pk}),
            {"book_submit": "True",
             "title": "rua_proposal_title updated",
             "subtitle": "rua_proposal_subtitle",
             "author": "rua_user",
             "rua_element": "example",
             "rua_element_2": "example"})
        content = resp.content
        self.assertEqual("403" in content, False)
        proposals = submission_models.Proposal.objects.filter(
            owner__isnull=True)
        proposal = proposals[0]
        self.assertEqual(proposal.title, "rua_proposal_title updated")
        resp = self.client.get(
            reverse('proposal_assign_user',
                   kwargs={'proposal_id': proposal.pk,
                           'user_id': 1})
        )
        content = resp.content

        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        proposals = submission_models.Proposal.objects.filter(
            owner__isnull=True)
        self.assertEqual(proposals.count(), 0)

    def test_proposal_history(self):
        # A proposal with the title 'rua_proposal_title'
        # has bee loaded from a fixture
        resp = self.client.get(reverse('proposals_history'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("rua_proposal_title" in content, True)

    def test_start_proposal_review(self):
        proposal = submission_models.Proposal.objects.get(pk=2)
        self.assertEqual(
            proposal.title,
            'rua_proposal_title',
            'The title of proposal with pk=2 does not match the fixture..'
        )

        # Creating a proposal review
        resp = self.client.post(
            reverse('start_proposal_review',
                    kwargs={'proposal_id': proposal.id}),
            {'due_date': '2016-04-29',
             'review_form': '1',
             'indv-reviewer_length': '5',
             'comm-reviewer_length': '5',
             'email_text': 'Test',
             'reviewer': ['4', '1'],
             'committee': ['2']}
        )
        self.assertEqual(resp.status_code, 302)

        proposal.refresh_from_db()
        self.assertFalse(
            proposal.date_review_started is None,
            'The proposal for which this test attempted to start a review has '
            'no review start date (date_review_started is None).'
        )
        self.assertEqual(proposal.review_assignments.count(), 2)

    def test_view_proposal_review_decision(self):
        # Initialisation
        proposal = submission_models.Proposal.objects.get(pk=2)
        resp = self.client.post(
            reverse('start_proposal_review',
                    kwargs={'proposal_id': proposal.id}),
            {'due_date': '2016-04-29',
             'review_form': '1',
             'indv-reviewer_length': '5',
             'comm-reviewer_length': '5',
             'email_text': 'Test',
             'reviewer': ['4', '1'],
             'committee': ['2']}
        )
        proposal_review_assignments = proposal.review_assignments.all()

        # Testing acceptance and declination of proposal by assigned reviewers
        resp = self.client.get(
            reverse('view_proposal_review_decision',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[0].id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        self.client.post(
            reverse('view_proposal_review_decision',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[0].id}),
            {'accept': ''}
        )
        self.client.post(
            reverse('view_proposal_review_decision',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[1].id}),
            {'decline': ''}
        )
        self.assertTrue(proposal_review_assignments[0].accepted is not None)
        self.assertFalse(proposal_review_assignments[0].declined is not None)
        self.assertTrue(proposal_review_assignments[1].declined is not None)
        self.assertFalse(proposal_review_assignments[1].accepted is not None)

        resp = self.client.get(
            reverse('view_proposal_review',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[0].id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertFalse("403" in content)

        resp = self.client.post(
            reverse(
                'view_proposal_review',
                kwargs={
                    'proposal_id': proposal.id,
                    'assignment_id': proposal_review_assignments[0].id}
                ),
            {
                'rua_name': 'example',
                'recommendation': 'accept',
                'competing_interests': 'nothing'
            }
        )
        proposal_review_assignments[0].refresh_from_db()
        self.assertTrue(proposal_review_assignments[0].completed is not None)

    def test_reopen_proposal_review(self):
        # Initialisation
        proposal = submission_models.Proposal.objects.get(pk=2)
        self.client.post(
            reverse('start_proposal_review',
                    kwargs={'proposal_id': proposal.id}),
            {'due_date': '2016-04-29',
             'review_form': '1',
             'indv-reviewer_length': '5',
             'comm-reviewer_length': '5',
             'email_text': 'Test',
             'reviewer': ['4', '1'],
             'committee': ['2']}
        )
        proposal_review_assignments = proposal.review_assignments.all()

        self.client.post(
            reverse('view_proposal_review_decision',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[0].id}),
            {'accept': ''}
        )
        self.client.post(
            reverse(
                'view_proposal_review',
                kwargs={
                    'proposal_id': proposal.id,
                    'assignment_id': proposal_review_assignments[0].id}
                ),
            {
                'rua_name': 'example',
                'recommendation': 'accept',
                'competing_interests': 'nothing'
            }
        )

        # Testing reopen_proposal_review function
        resp = self.client.get(
            reverse('reopen_proposal_review',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[0].id})
        )
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertFalse("403" in content)

        resp = self.client.post(
            reverse(
                'reopen_proposal_review',
                kwargs={
                    'proposal_id': proposal.id,
                    'assignment_id': proposal_review_assignments[0].id
                }
            ),
            {
                'due_date': '2015-11-11',
                'email': 'test',
                'comments': 'testing'
            }
        )
        proposal_review_assignments[0].refresh_from_db()

        self.assertTrue(proposal_review_assignments[0].reopened)

        resp = self.client.get(
            reverse('view_proposal_review',
                    kwargs={'proposal_id': proposal.id,
                            'assignment_id': proposal_review_assignments[0].id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse(
                'view_proposal_review',
                kwargs={
                    'proposal_id': proposal.id,
                    'assignment_id': proposal_review_assignments[0].id
                }
            ),
            {'rua_name': 'example',
             'recommendation': 'accept',
             'competing_interests': 'nothing'}
        )
        proposal_review_assignments[0].refresh_from_db()
        self.assertFalse(proposal_review_assignments[0].reopened)

    def test_readonly_profile(self):
        resp = self.client.get(
            reverse('view_profile_readonly', kwargs={'user_id': 1}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("/user/profile/update/" in content, False)
        self.assertEqual("/user/profile/resetpassword/" in content, False)

    """ Form Tests """

    def test_update_profile(self):
        resp = self.client.post(reverse('update_profile'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(reverse('update_profile'),
                                {'first_name': 'new', 'institution': "Testing",
                                 'country': "GB"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/user/profile/")

    def test_register(self):
        resp = self.client.post(
            reverse('register'),
            {'first_name': 'new',
             'last_name': 'last',
             'username': 'user1',
             'email': 'fake@faked.com',
             'password1': 'password1',
             'password2': "password1",
             'institution': 'Institute of Testable Hypotheses',
             'country': 'GB'}
        )
        self.assertEqual(resp.status_code, 302)

        self.assertEqual(resp['Location'], "http://testing/login/")

    def test_reset_password(self):
        resp = self.client.post(reverse('reset_password'),
                                {'password_1': 'password1',
                                 'password_2': "password1"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "http://testing/login/")

    def test_reset_password_no_match(self):
        resp = self.client.post(reverse('reset_password'),
                                {'password_1': 'password1',
                                 'password_2': "password12"})
        self.assertEqual(resp.status_code, 200)
        message = self.get_specific_message(resp, 0)
        self.assertEqual(str(message), 'Your passwords do not match.')
        resp = self.client.post(reverse('reset_password'),
                                {'password_1': 'pass', 'password_2': "pass"})
        self.assertEqual(resp.status_code, 200)
        message = self.get_specific_message(resp, 0)
        self.assertEqual(str(message),
                         'Password is not long enough, must be greater than 8 characters.')

    def test_register_login(self):
        resp = self.client.post(
            reverse('register'),
            {'first_name': 'new',
             'last_name': 'last',
             'username': 'user1',
             'email': 'fake@faked.com',
             'password1': 'password1',
             'password2': "password1",
             'institution': 'Institute of Testable Hypotheses',
             'country': 'GB'})
        self.assertEqual(resp.status_code, 302)

        user = User.objects.get(username="user1")
        roles = models.Role.objects.filter(name__icontains="Editor")
        for role in roles:
            user.profile.roles.add(role)
        user.active = True
        user.save()
        user.profile.save()
        resp = self.client.post(reverse('login'), {'user_name': 'user1',
                                                   'user_pass': "password1"})
        self.assertEqual(resp['Location'], "http://testing/dashboard/")

    def test_upload_misc_file(self):

        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        resp = self.client.get(
            reverse('upload_misc_file', kwargs={'submission_id': self.book.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Upload Misc File" in content, True)

        misc_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(
            reverse('upload_misc_file', kwargs={'submission_id': self.book.id}),
            {'file_type': 'other', 'label': 'test', 'misc_file': misc_file})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'],
                         "http://testing/editor/submission/1/")

    def test_upload_manuscript_file(self):

        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        resp = self.client.get(reverse('upload_manuscript',
                                       kwargs={'submission_id': self.book.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Upload Manuscript File" in content, True)

        manuscript_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(reverse('upload_manuscript',
                                        kwargs={'submission_id': self.book.id}),
                                {'file_type': 'other', 'label': 'test',
                                 'manuscript': manuscript_file})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'],
                         "http://testing/editor/submission/1/")

    def test_upload_additional_file(self):

        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        resp = self.client.get(reverse('upload_additional',
                                       kwargs={'submission_id': self.book.id}))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("Upload Additional File" in content, True)

        additional_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(reverse('upload_additional',
                                        kwargs={'submission_id': self.book.id}),
                                {'file_type': 'other', 'label': 'test',
                                 'additional': additional_file})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'],
                         "http://testing/editor/submission/1/")

    def test_delete_file(self):

        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        manuscript_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(reverse('upload_manuscript',
                                        kwargs={'submission_id': self.book.id}),
                                {'file_type': 'other', 'label': 'test',
                                 'manuscript': manuscript_file})

        resp = self.client.get(reverse('delete_file',
                                       kwargs={'submission_id': self.book.id,
                                               'file_id': 1,
                                               'returner': 'new'}))
        content = resp.content

        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)

        self.assertEqual(resp['Location'],
                         "http://testing/editor/submission/1/")
        resp = self.client.get(reverse('delete_file',
                                       kwargs={'submission_id': self.book.id,
                                               'file_id': 1,
                                               'returner': 'new'}))
        content = resp.content

        self.assertEqual(resp.status_code, 404)

    def test_update_file(self):

        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        manuscript_file = tempfile.NamedTemporaryFile(delete=False)
        resp = self.client.post(reverse('upload_manuscript',
                                        kwargs={'submission_id': self.book.id}),
                                {'file_type': 'other', 'label': 'test',
                                 'manuscript': manuscript_file})

        resp = self.client.get(reverse('view_file',
                                       kwargs={'submission_id': self.book.id,
                                               'file_id': 1}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.get(reverse('update_file',
                                       kwargs={'submission_id': self.book.id,
                                               'file_id': 1,
                                               'returner': 'new'}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(reverse('update_file',
                                        kwargs={'submission_id': self.book.id,
                                                'file_id': 1,
                                                'returner': 'new'}),
                                {'rename': 'new_label'})
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        resp = self.client.get(reverse('versions_file',
                                       kwargs={'submission_id': self.book.id,
                                               'file_id': 1}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

    """ Email tests """

    def test_email(self):
        self.author = models.Author.objects.get(pk=1)
        self.book = models.Book.objects.get(pk=1)
        self.book.save()
        onetaskers = self.book.onetaskers()

        # check that it exists in the database
        self.assertEqual(len(models.Book.objects.all()) == 1, True)
        resp = self.client.get(
            reverse('email_users',
                    kwargs={'group': 'all',
                            'submission_id': str(self.book.id)})
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content
        self.assertEqual("403" in content, False)
        resp = self.client.post(
            reverse('email_users',
                    kwargs={'group': 'all',
                            'submission_id': str(self.book.id)
                            }),
            {'subject': 'all',
             'to_values': self.author.author_email,
             "cc_values": "",
             "bcc_values": "",
             "body": 'text'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("was sent" in resp.content, True)
        resp = self.client.post(
            reverse('email_user',
                    kwargs={'group': 'editors',
                            'submission_id': str(self.book.id),
                            'user_id': self.user.id}),
            {'subject': 'all',
             'to_values': self.user.email,
             "cc_values": "",
             "bcc_values": "",
             "body": 'text'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("was sent" in resp.content, True)
        resp = self.client.get(
            reverse('email_user',
                    kwargs={'group': 'editors',
                            'submission_id': str(self.book.id),
                            'user_id': self.user.id})
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content
        self.assertEqual("403" in content, False)
        resp = self.client.get(
            reverse('email_user',
                    kwargs={'group': 'authors',
                            'submission_id': str(self.book.id),
                            'user_id': self.author.id})
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content
        self.assertEqual("403" in content, False)
        resp = self.client.get(
            reverse('email_user',
                    kwargs={'group': 'onetaskers',
                            'submission_id': str(self.book.id),
                            'user_id': onetaskers[0].id})
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content
        self.assertEqual("403" in content, False)
        resp = self.client.get(
            reverse('email_user',
                    kwargs={'group': 'onetaskers',
                            'submission_id': str(self.book.id),
                            'user_id': 15})
        )
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(
            reverse('email_user',
                    kwargs={'group': 'editors',
                            'submission_id': str(self.book.id),
                            'user_id': 15})
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content
        self.assertEqual("403" in content, False)
        message = self.get_specific_message(resp, 0)
        self.assertEqual(str(message), 'This editor was not found')
        resp = self.client.get(
            reverse('email_users',
                    kwargs={'group': 'unknown',
                            'submission_id': str(self.book.id)})
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp['Location'],
            "http://testing/email/all/submission/1/",
        )

        resp = self.client.post(
            reverse('proposal_start'),
            {
                "book_submit": "True",
                "title": "rua_proposal_title",
                "subtitle": "rua_proposal_subtitle",
                "author": "rua_user",
                "rua_element": "example",
                "rua_element_2": "example"
            }
        )
        resp = self.client.get(
            reverse('email_user_proposal',
                    kwargs={'user_id': 1,
                            'proposal_id': 1}),
            {'subject': 'all',
             'to_values': self.author.author_email,
             "cc_values": "",
             "bcc_values": "",
             "body": 'text'}
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(
            reverse('email_user_proposal',
                    kwargs={'user_id': 1,
                            'proposal_id': 1}),
            {'subject': 'all',
             'to_values': self.author.author_email,
             "cc_values": "",
             "bcc_values": "",
             "body": 'text'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("was sent" in resp.content, True)

    def test_book_get_all_editors_no_editors(self):
        book = BookFactory(title='Transatlantic Testing Networks')

        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            0,
            'A non-empty list was returned for a book with no editors assigned.'
        )

    def test_book_get_all_editors_press_editor(self):
        book = BookFactory(title='Transatlantic Testing Networks')
        press_editor = UserFactory(username='Preston')

        book.press_editors = [press_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            1,
            'A list with a length other than 1 was returned for a book '
            'with one editor assigned.'
        )
        self.assertTrue(
            press_editor in editors,
            'The press editor assigned to a book was not '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_series_editor(self):
        book = BookFactory(title='Transatlantic Testing Networks')
        series_editor = UserFactory(username='Saul')
        series = SeriesFactory(
            name='Global Guides to Testing',
            editor=series_editor
        )

        book.series = series
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            1,
            'A list with a length other than 1 was returned for a book '
            'with one editor assigned.'
        )
        self.assertTrue(
            series_editor in editors,
            'The series editor assigned to a book was not in '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_book_editor(self):
        book = BookFactory(title='Transatlantic Testing Networks')
        book_editor = UserFactory(username='Edmund')

        book.press_editors = [book_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            1,
            'A list with a length other than 1 was returned for a book '
            'with one editor assigned.'
        )
        self.assertTrue(
            book_editor in editors,
            'The book editor assigned to a book was not '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_press_and_series_editors(self):
        press_editor = UserFactory(username='Preston')
        series_editor = UserFactory(username='Saul')
        series = SeriesFactory(
            name='Global Guides to Testing',
            editor=series_editor
        )
        book = BookFactory(title='Transatlantic Testing Networks')

        book.series = series
        book.press_editors = [press_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            2,
            'A list with a length other than 2 was returned for a book '
            'with two editors assigned.'
        )
        self.assertTrue(
            series_editor in editors,
            'The series editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            press_editor in editors,
            'The press editor assigned to a book was not in '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_press_and_book_editors(self):
        press_editor = UserFactory(username='Preston')
        book_editor = UserFactory(username='Edmund')
        book = BookFactory(title='Transatlantic Testing Networks')

        book.press_editors = [press_editor]
        book.book_editors = [book_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            2,
            'A list with a length other than 2 was returned for a book '
            'with two editors assigned.'
        )
        self.assertTrue(
            book_editor in editors,
            'The book editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            press_editor in editors,
            'The press editor assigned to a book was not in '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_series_and_book_editors(self):
        series_editor = UserFactory(username='Saul')
        book_editor = UserFactory(username='Edmund')
        series = SeriesFactory(
            name='Global Guides to Testing',
            editor=series_editor
        )
        book = BookFactory(title='Transatlantic Testing Networks')

        book.series = series
        book.book_editors = [book_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            2,
            'A list with a length other than 2 was returned for a book '
            'with two editors assigned.'
        )
        self.assertTrue(
            series_editor in editors,
            'The series editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            book_editor in editors,
            'The book editor assigned to a book was not in '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_all_editor_types(self):
        press_editor = UserFactory(username='Preston')
        series_editor = UserFactory(username='Saul')
        book_editor = UserFactory(username='Edmund')
        series = SeriesFactory(
            name='Global Guides to Testing',
            editor=series_editor
        )
        book = BookFactory(title='Transatlantic Testing Networks')

        book.series = series
        book.press_editors = [press_editor]
        book.book_editors = [book_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            3,
            'A list with a length other than 3 was returned for a book '
            'with three editors assigned.'
        )
        self.assertTrue(
            series_editor in editors,
            'The series editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            press_editor in editors,
            'The press editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            book_editor in editors,
            'The book editor assigned to a book was not in '
            'the list of editors returned.'
        )

    def test_book_get_all_editors_ensure_no_duplicates(self):
        press_editor = UserFactory(username='Preston')
        series_editor = UserFactory(username='Saul')
        book_editor = UserFactory(username='Edmund')
        series = SeriesFactory(
            name='Global Guides to Testing',
            editor=series_editor
        )
        book = BookFactory(title='Transatlantic Testing Networks')

        book.series = series
        book.press_editors = [press_editor, series_editor]
        book.book_editors = [press_editor, book_editor]
        book.save()
        editors = book.get_all_editors()

        self.assertEqual(
            len(editors),
            3,
            'A list with a length other than 3 was returned for a book '
            'with three unique editors assigned (5 in total, 2 duplicates).'
        )
        self.assertTrue(
            series_editor in editors,
            'The series editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            press_editor in editors,
            'The press editor assigned to a book was not in '
            'the list of editors returned.'
        )
        self.assertTrue(
            book_editor in editors,
            'The book editor assigned to a book was not in '
            'the list of editors returned.'
        )
