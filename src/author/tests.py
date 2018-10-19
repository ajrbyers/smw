import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone

from core import models as core_models


class AuthorTests(TestCase):

    # Dummy DBs
    fixtures = [
        'settinggroups',
        'settings/master',
        'langs',
        'cc-licenses',
        'role',
        'forms/master',
        'test/test_auth_data',
        'test/test_core_data',
        'test/test_review_data',
        'test/test_copyedit_assignment_data',
        'test/test_index_assignment_data',
        'test/test_contract_data',
    ]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username="rua_author")
        self.user.save()
        self.book = core_models.Book.objects.get(pk=1)

        login = self.client.login(
            username=self.user.username, password="tester"
        )
        self.assertEqual(login, True)

    def tearDown(self):
        pass

    def test_dashboard(self):
        resp = self.client.get(reverse('author_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

    def test_submission(self):
        resp = self.client.get(
            reverse(
                'author_submission',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"AUTHORS" in content, True)
        authors = self.book.author.all()
        for author in authors:
            self.assertEqual(
                bytes(author.full_name(), encoding='ascii') in content, True
            )
        self.assertEqual(b"DESCRIPTION" in content, True)
        self.assertEqual(
            bytes(self.book.description, encoding='ascii') in content, True
        )
        self.assertEqual(b"COVER LETTER" in content, True)
        self.assertEqual(
            bytes(self.book.cover_letter, encoding='ascii') in content, True
        )
        self.assertEqual(b"REVIEWER SUGGESTIONS" in content, True)
        self.assertEqual(
            bytes(self.book.reviewer_suggestions, encoding='ascii') in content,
            True
        )
        self.assertEqual(b"COMPETING INTERESTS" in content, True)
        self.assertEqual(
            bytes(self.book.competing_interests, encoding='ascii') in content,
            True
        )

    def test_submission_status(self):
        resp = self.client.get(
            reverse(
                'status',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Current Status" in content, True)
        self.assertEqual(b"Submission Progress" in content, True)
        self.assertEqual(b"Review" in content, True)
        self.assertEqual(b"Submission" in content, True)

    def test_submission_tasks_no_data(self):
        # Clear assignments from fixture test/test_copyedit_assignment_data.json
        for assignment in core_models.CopyeditAssignment.objects.all():
            assignment.delete()

        resp = self.client.get(
            reverse('tasks',
                    kwargs={'submission_id': self.book.id}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"My Tasks" in content, True)
        self.assertEqual(b"<h5>No outstanding tasks</h5>" in content, True)
        self.typeset_assignment = core_models.TypesetAssignment.objects.get(
            pk=1
        )
        self.typeset_assignment.author_invited = timezone.now()
        self.typeset_assignment.save()

        resp = self.client.get(reverse('tasks',
                                       kwargs={'submission_id': self.book.id}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"My Tasks" in content, True)
        self.assertEqual(b"No outstanding tasks" in content, False)
        self.assertEqual(b"Typesetting Review" in content, True)

    def test_submission_tasks(self):
        # Fixture data from test/test_copyedit_assignment_data.json is retained
        self.client.login(username="rua_editor", password="tester")
        resp = self.client.post(
            reverse('request_revisions',
                    kwargs={'submission_id': self.book.id,
                            'returner': 'review'}),
            {'notes_from_editor': 'notes',
             'due': '2015-11-30',
             'id_email_text': 'Hi User'}
        )
        self.assertFalse(
            b'There is already an outstanding revision request for this book'
            in resp.content
        )
        self.assertEqual(resp.status_code, 302)

        copyedit = core_models.CopyeditAssignment.objects.get(pk=1)
        copyedit.author_completed = None
        copyedit.author_invited = timezone.now()
        copyedit.save()

        self.client.login(username="rua_author", password="tester")
        resp = self.client.get(reverse('tasks',
                                       kwargs={'submission_id': self.book.id}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertTrue(b"Revisions Requested" in content)
        self.assertTrue(b"Copyedit Review" in content)

    def test_review_assignment(self):
        resp = self.client.get(
            reverse(
                'view_review_assignment',
                kwargs={
                    'submission_id': self.book.id,
                    'round_id': 1, 'review_id': 1
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

    def test_author_review_review_round(self):
        review_assignment = core_models.ReviewAssignment.objects.get(pk=1)
        review_assignment.review_round = None
        review_assignment.save()
        resp = self.client.get(
            reverse(
                'review',
                kwargs={
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.review_round = core_models.ReviewRound.objects.get(
            book=self.book,
            round_number=1
        )
        resp = self.client.get(
            reverse(
                'review',
                kwargs={
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"btn-task" in content, True)
        resp = self.client.get(
            reverse(
                'view_review_round',
                kwargs={
                    'round_id': 1,
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"btn-task" in content, True)
        self.assertEqual(b"ROUND 1" in content, True)

    def test_author_editing(self):
        self.book.stage.current_stage = 'editing'
        self.book.stage.editing = timezone.now()
        self.book.stage.save()
        self.book.save()
        resp = self.client.get(
            reverse(
                'editing',
                kwargs={
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"COPYEDITING" in content, True)
        self.assertEqual(b"INDEXING" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, True)
        self.book.stage.copyediting = timezone.now()
        self.book.stage.indexing = timezone.now()
        self.book.stage.save()
        self.book.save()
        resp = self.client.get(
            reverse(
                'editing',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"COPYEDITING" in content, True)
        self.assertEqual(b"INDEXING" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, False)

        copyedit = core_models.CopyeditAssignment.objects.get(pk=1)
        copyedit.author_completed = None
        copyedit.author_invited = timezone.now()
        copyedit.save()
        resp = self.client.get(
            reverse(
                'author_view_copyedit',
                kwargs={
                    'copyedit_id': 1,
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"COPYEDITING" in content, True)
        self.assertEqual(b"INDEXING" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, False)
        self.assertEqual(b"COPYEDIT ASSIGNMENT: 1" in content, True)
        self.client.login(username="rua_onetasker", password="tester")
        self.client.post(
            reverse(
                'onetasker_task_hub',
                kwargs={
                    'assignment_type': 'copyedit',
                    'assignment_id': 1
                }
            ),
            {'decision': 'accept'}
        )
        file_test, _ = tempfile.mkstemp()
        self.client.post(
            reverse(
                'onetasker_task_hub',
                kwargs={
                    'assignment_type': 'copyedit',
                    'assignment_id': 1
                }
            ),
            {
                'task': '', 'note':
                'notes', 'file_upload': file_test
            }
        )
        self.client.login(username="rua_author", password="tester")
        resp = self.client.get(reverse('author_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Copyedit Review" in content, True)
        resp = self.client.get(
            reverse(
                'copyedit_review',
                kwargs={
                    'copyedit_id': 1,
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        resp = self.client.post(
            reverse(
                'copyedit_review',
                kwargs={
                    'copyedit_id': 1,
                    'submission_id': self.book.id
                }
            ),
            {'notes_from_author': 'notes'}
        )
        copyedit = core_models.CopyeditAssignment.objects.get(pk=1)
        self.assertEqual(copyedit.completed is None, False)
        resp = self.client.get(
            reverse(
                'author_view_index',
                kwargs={
                    'index_id': 1,
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"COPYEDITING" in content, True)
        self.assertEqual(b"INDEXING" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, False)
        self.assertEqual(b"INDEX ASSIGNMENT: 1" in content, True)

    def test_author_production(self):
        self.book.stage.current_stage = 'production'
        self.book.stage.production = timezone.now()
        self.book.stage.save()
        self.book.save()
        resp = self.client.get(
            reverse(
                'author_production',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Typesetting" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, True)
        self.book.stage.typesetting = timezone.now()
        self.book.stage.save()
        self.book.save()
        resp = self.client.get(
            reverse(
                'author_production',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Typesetting" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, False)

        resp = self.client.get(
            reverse(
                'author_view_typesetter',
                kwargs={
                    'typeset_id': 1,
                    'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Typesetting" in content, True)
        self.assertEqual(b"Stage has not been initialised." in content, False)
        self.assertEqual(b"TYPESET ASSIGNMENT: 1" in content, True)
        typeset = core_models.TypesetAssignment.objects.get(pk=1)
        typeset.author_completed = None
        typeset.completed = None
        typeset.author_invited = timezone.now()
        typeset.save()
        self.client.login(username="rua_onetasker", password="tester")
        self.client.post(
            reverse(
                'onetasker_task_hub',
                kwargs={
                    'assignment_type': 'typesetting',
                    'assignment_id': 1
                }
            ),
            {'decision': 'accept'}
        )
        file_test, _ = tempfile.mkstemp()
        self.client.post(
            reverse(
                'onetasker_task_hub',
                kwargs={
                    'assignment_type': 'typesetting',
                    'assignment_id': 1
                }
            ),
            {
                'task': '',
                 'note_from_typesetter': 'notes',
                 'file_upload': file_test
             }
        )
        self.client.login(username="rua_author", password="tester")
        resp = self.client.get(reverse('author_dashboard'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Typesetting Review" in content, True)
        resp = self.client.get(
            reverse(
                'typeset_review',
                kwargs={
                    'typeset_id': 1,
                    'submission_id': self.book.id
                }
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        resp = self.client.post(
            reverse(
                'typeset_review',
                kwargs={
                    'typeset_id': 1,
                    'submission_id': self.book.id}
            ),
            {'notes_from_author': 'notes'}
        )
        typeset = core_models.TypesetAssignment.objects.get(pk=1)
        self.assertEqual(typeset.completed is None, False)

    def test_contract_sign_off(self):
        self.book.contract = core_models.Contract.objects.get(pk=1)
        self.book.save()
        resp = self.client.get(
            reverse(
                'author_submission',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Sign Off" in content, False)
        self.book.contract.author_signed_off = None
        self.book.contract.save()
        resp = self.client.get(
            reverse(
                'author_submission',
                kwargs={'submission_id': self.book.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Sign Off" in content, True)
        resp = self.client.get(
            reverse(
                'author_contract_signoff',
                kwargs={
                    'submission_id': self.book.id,
                    'contract_id': self.book.contract.id}
            )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        contract_file = tempfile.NamedTemporaryFile(delete=False)
        self.client.post(
            reverse(
                'author_contract_signoff',
                kwargs={
                    'submission_id': self.book.id,
                    'contract_id': self.book.contract.id
                }
            ),
            {
                'next_stage': '',
                'author_file': contract_file
            }
        )
        contract = core_models.Contract.objects.get(pk=1)
        self.assertEqual(contract.author_signed_off is None, False)
