from django.test import TestCase
from submission import models
from django.utils import timezone
from core import models as core_models
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.core import management


class SubmissionTests(TestCase):
    # Dummy DBs
    fixtures = [
        'settinggroups',
        'settings',
        'langs',
        'cc-licenses',
        'role',
        'test/test_auth_data',
        'test/test_review_data',
        'test/test_core_data',
        'test/test_index_assignment_data',
        'test/test_copyedit_assignment_data',
        'test/test_manager_data',
        'test/test_submission_checklist_item_data',
        'test/test_proposal_form',
        'test/test_incomplete_proposal',
        'test/test_files'
    ]

    # Helper Function

    def getmessage(cls, response):
        """Helper method to return first message from response """
        for c in response.context:
            message = [m for m in c.get('messages')][0]
            if message:
                return message

    def setUp(self):
        self.client = Client(HTTP_HOST="testing")
        self.user = User.objects.get(username="rua_user")
        self.user.save()
        self.book = core_models.Book.objects.get(pk=1)

        login = self.client.login(username="rua_user", password="root")
        self.assertEqual(login, True)

    def tearDown(self):
        pass

    def test_set_up(self):
        """
        testing set up
        """
        self.assertEqual(self.user.username == "rua_user", True)
        self.assertEqual(self.user.email == "fake_user@fakeaddress.com", True)
        self.assertEqual(self.user.first_name == "rua_user_first_name", True)
        self.assertEqual(self.user.last_name == "rua_user_last_name", True)
        self.assertEqual(self.user.profile.institution == "rua_testing", True)
        self.assertEqual(self.user.profile.country == "GB", True)

    def test_submission_proposal(self):
        resp = self.client.get(reverse('proposal_start'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        proposal_form = core_models.ProposalForm.objects.filter(active=True).first()
        fields = core_models.ProposalFormElementsRelationship.objects.filter(
            form=proposal_form)
        self.assertEqual('name="title"' in content, True)
        self.assertEqual('name="subtitle"' in content, True)
        self.assertEqual('name="author"' in content, True)

        for field in fields:
            self.assertEqual('name="%s"' % field.element.name in content, True)

        self.assertEqual(models.Proposal.objects.count(), 0)

        resp = self.client.post(
            reverse('proposal_start'),
                    {"book_submit": "True",
                     "title": "rua_proposal_title",
                     "subtitle": "rua_proposal_subtitle",
                     "author": "rua_user", "rua_element": "example",
                     "rua_element_2": "example"}
        )
        self.assertEqual(models.Proposal.objects.count(), 1)
        new_proposal = models.Proposal.objects.get(title='rua_proposal_title')

        resp = self.client.get(
            reverse('proposal_view_submitted',
                    kwargs={"proposal_id": new_proposal.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('proposal_view_submitted',
                    kwargs={"proposal_id": new_proposal.id}),
            {"book_submit": "True",
             "title": "rua_proposal_title",
             "subtitle": "rua_proposal_subtitle",
             "author": "rua_user",
             "rua_element": "example",
             "rua_element_2": "example"}
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('proposal_history_submitted',
                    kwargs={"proposal_id": new_proposal.id}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('proposal_history_view_submitted',
                    kwargs={"proposal_id": new_proposal.id,
                            'history_id': 1}
                    )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        notes = models.ProposalNote.objects.all()
        self.assertEqual(notes.count(), 0)
        resp = self.client.get(
            reverse('submission_notes_add',
                    kwargs={"proposal_id": new_proposal.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('submission_notes_add',
                    kwargs={"proposal_id": new_proposal.id}),
            {"text": "note_test"}
        )
        notes = models.ProposalNote.objects.all()
        self.assertEqual(notes.count(), 1)

        resp = self.client.get(
            reverse('submission_notes_view',
                    kwargs={"proposal_id": new_proposal.id,
                            "note_id": 1})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('submission_notes_update',
                    kwargs={"proposal_id": new_proposal.id,
                            "note_id": 1})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('submission_notes_update',
                    kwargs={"proposal_id": new_proposal.id,
                            "note_id": 1}),
                    {"text": "note_test"}
        )
        content = resp.content
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('proposal_revisions',
                    kwargs={"proposal_id": new_proposal.id})
        )
        self.assertEqual(resp.status_code, 404)

        new_proposal.refresh_from_db()
        new_proposal.status = 'revisions_required'
        new_proposal.requestor = self.user
        new_proposal.revision_due_date = timezone.now()
        new_proposal.save()

        resp = self.client.get(
            reverse('proposal_revisions',
                    kwargs={"proposal_id": new_proposal.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        resp = self.client.post(
            reverse('proposal_revisions',
                    kwargs={"proposal_id": new_proposal.id}),
            {"title": "updated",
             "subtitle": "rua_proposal_subtitle",
             "author": "rua_user",
             "rua_element": "changed",
             "rua_element_2": "changed"}
        )

        new_proposal.refresh_from_db()
        self.assertEqual("updated", new_proposal.title)
        self.assertEqual('revisions_submitted', new_proposal.status)

    def test_incomplete_proposal(self):
        incomplete_proposal = models.IncompleteProposal.objects.first()

        resp = self.client.get(
            reverse('incomplete_proposal',
                    kwargs={"proposal_id": incomplete_proposal.id}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('incomplete_proposal',
                    kwargs={"proposal_id": incomplete_proposal.id}),
            {"incomplete": "True",
             "title": "rua_proposal_title",
             "subtitle": "rua_proposal_subtitle",
             "author": "rua_user",
             "rua_element": "example",
             "rua_element_2": "example"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        forms = models.IncompleteProposal.objects.all()
        self.assertEqual(forms.count(), 1)
        resp = self.client.post(
            reverse('incomplete_proposal',
                    kwargs={"proposal_id": incomplete_proposal.id}),
            {"book_submit": "True",
             "title": "rua_proposal_title",
             "subtitle": "rua_proposal_subtitle",
             "author": "rua_user",
             "rua_element": "example",
             "rua_element_2": "example"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        forms = models.IncompleteProposal.objects.all()
        self.assertEqual(forms.count(), 0)
        resp = self.client.post(
            reverse('proposal_start'),
            {
                "incomplete": "True",
                 "title": "rua_proposal_title",
                 "subtitle": "rua_proposal_subtitle",
                 "author": "rua_user", "rua_element": "example",
                 "rua_element_2": "example"
            }
        )

        forms = models.IncompleteProposal.objects.all()
        self.assertEqual(forms.count(), 1)

    def test_submission_book(self):
        setting = core_models.Setting.objects.get(name="direct_submissions")
        setting.value = None
        setting.save()

        resp = self.client.get(reverse('submission_start'))
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/proposal/"
        )
        setting = core_models.Setting.objects.get(name="direct_submissions")
        setting.value = 'on'
        setting.save()

        resp = self.client.get(reverse('submission_start'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        # Create first book by submission
        resp = self.client.post(
            reverse('submission_start'),
            {
                "book_type": "monograph",
                 "license": "2",
                 "review_type": "open-with",
                 "cover_letter": "rua_cover_letter",
                 "reviewer_suggestions": "rua_suggestion",
                 "competing_interests": "rua_competing_interest",
                 "item": True,
                 "item2": True
            }
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)

        monograph_submission =  core_models.Book.objects.filter(
            book_type='monograph').exclude(id=self.book.id).first()
        self.assertEqual(
            resp['Location'],
             "http://testing/submission/book/{book_id}/stage/2/".format(
                 book_id=monograph_submission.id
             )
        )

        resp = self.client.post(
            reverse('submission_start'),
            {
                'title': 'edited_volume',
                "book_type": "edited_volume",
                 "license": "2",
                 "review_type": "open-with",
                 "cover_letter": "rua_cover_letter",
                 "reviewer_suggestions": "rua_suggestion",
                 "competing_interests": "rua_competing_interest",
                 "item": True,
                 "item2": True
            }
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)

        edited_volume_submission = core_models.Book.objects.filter(
            book_type='edited_volume').exclude(id=self.book.id).first()
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/{book_id}/stage/2/".format(
                book_id=edited_volume_submission.id
            )
        )

        self.book.owner = self.user
        self.book.save()

        resp = self.client.post(
            reverse('edit_start',
                    kwargs={"book_id": self.book.id}),
            {
                "book_type": "monograph",
                 "license": "2",
                 "review_type": "open-with",
                 "cover_letter": "rua_cover_letter_updated",
                 "reviewer_suggestions": "rua_suggestion",
                 "competing_interests": "rua_competing_interest",
                 "item": True,
                 "item2": True
            }
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/1/stage/2/"
        )

        resp = self.client.post(
            reverse('edit_start',
                    kwargs={"book_id": monograph_submission.id}),
            {
                "book_type": "monograph",
                 "license": "2",
                 "review_type": "open-with",
                 "cover_letter": "rua_cover_letter_updated",
                 "reviewer_suggestions": "rua_suggestion",
                 "competing_interests": "rua_competing_interest",
                 "item": True,
                 "item2": True
            }
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/{book_id}/stage/2/".format(
                book_id=monograph_submission.id
            )
        )
        resp = self.client.get(
            reverse('submission_two',
                    kwargs={"book_id": monograph_submission.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('submission_two',
                    kwargs={"book_id": monograph_submission.id}),
            {
                "title": "new_book_title",
                 "subtitle": "new_book_subtitle",
                 "prefix": "new_book_prefix",
                 "description": "rua_description"
            }
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/{book_id}/stage/3/".format
                (
                    book_id=monograph_submission.id
                )
        )

        resp = self.client.post(
            reverse('submission_two',
                    kwargs={"book_id": monograph_submission.id}),
            {
                "title": "new_book_title",
                 "subtitle": "new_book_subtitle",
                 "prefix": "new_book_prefix",
                 "description": "rua_description_updated"
            }
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/{book_id}/stage/3/".format(
                book_id=monograph_submission.id
            )
        )


        resp = self.client.get(
            reverse('submission_three',
                    kwargs={"book_id": self.book.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('submission_three', kwargs={"book_id": self.book.id}),
            {"next_stage": ""})
        self.assertEqual(resp.status_code, 302)
        self.book.files.add(core_models.File.objects.get(pk=1))
        self.book.files.add(core_models.File.objects.get(pk=2))
        self.book.save()
        resp = self.client.post(
            reverse('submission_three', kwargs={"book_id": self.book.id}),
            {"next_stage": ""})

        self.book.submission_stage = 4
        self.book.save()

        resp = self.client.get(
            reverse('submission_three_additional'
                    , kwargs={"book_id": self.book.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.post(
            reverse('submission_three_additional',
                    kwargs={"book_id": self.book.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.book.submission_stage = 5
        self.book.save()

        resp = self.client.get(
            reverse('submission_additional_files',
                    kwargs={"book_id": self.book.id,
                           'file_type': 'additional'}
                    )
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('submission_four',
                    kwargs={"book_id": self.book.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('author', kwargs={"book_id": self.book.id})
       )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)

        resp = self.client.get(
            reverse('author_edit',
                    kwargs={"book_id": self.book.id,
                            'author_id': self.book.author.first().id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual("403" in content, False)
        self.assertEqual("rua_user" in content, True)
        self.assertEqual("rua_testing" in content, True)

        resp = self.client.post(
            reverse('submission_four', kwargs={"book_id": self.book.id}),
            {"next_stage": ""})
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/{book_id}/stage/6/".format(
                book_id=self.book.id
            )
        )

        resp = self.client.get(
            reverse('submission_five', kwargs={"book_id": self.book.id}))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertFalse("403" in content)

        resp = self.client.post(
            reverse('submission_five',
                    kwargs={"book_id": self.book.id}),
            {"complete": ""}
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual("403" in content, False)
        self.assertEqual(
            resp['Location'],
            "http://testing/submission/book/1/submission-complete-email/"
        )
