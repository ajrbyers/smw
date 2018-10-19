from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from django.core.exceptions import ObjectDoesNotExist

from core import models as core_models
from manager import models
from review import models as review_models
from submission import models as submission_models


class ManagerTests(TestCase):
    # Dummy DBs
    fixtures = [
        'settinggroups',
        'settings/master',
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
    ]

    # Helper Function
    def getmessage(cls, response):
        """Helper method to return first message from response """
        for c in response.context:
            message = [m for m in c.get('messages')][0]
            if message:
                return message

    def setUp(self):
        self.client = Client()
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

    def test_manager_access_staff(self):
        resp = self.client.get(reverse('manager_index'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

    def test_manager_about(self):
        resp = self.client.get(reverse('manager_about'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

    def test_manager_access_not_staff(self):
        self.client.login(username="rua_reviewer", password="tester")
        resp = self.client.get(reverse('manager_index'))
        self.assertEqual(b"403 - Permission Denied" in resp.content, True)
        self.assertEqual(resp.status_code, 200)

    def test_clear_cache(self):
        resp = self.client.get(reverse('manager_flush_cache'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], "/manager/")
        resp = self.client.get(reverse('manager_index'))
        message = self.getmessage(resp)
        self.assertEqual(message.message, "Memcached has been flushed.")

    def test_manager_users(self):
        # users page
        users = User.objects.all()
        resp = self.client.get(reverse('manager_users'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(len(users), 5)
        for user in users:
            self.assertEqual(bytes(user.username, 'utf-8') in content, True)
        # add user
        resp = self.client.post(reverse('add_user'),
                                {'username': 'rua_new_user',
                                 'first_name': 'Usera', 'last_name': 'Lastly',
                                 'middle_name': 'Middler', 'roles': '2',
                                 'country': 'GB',
                                 'email': 'fake_new_user@fakeaddress.com',
                                 'department': 'test', 'signature': 'Hieee',
                                 'salutation': 'Mrs',
                                 'institution': 'rua_testing',
                                 'interests': 'gardening,ornithologyy,cats',
                                 'biography': 'bio'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'],
                         "/manager/user/?username=%s&password=%s" % (
                         "rua_new_user", "None"))

        try:
            new_user = User.objects.get(username="rua_new_user")
            found = True
        except:
            found = False
        self.assertEqual(found, True)
        users = User.objects.all()
        self.assertEqual(len(users), 6)
        # edit user
        resp = self.client.post(
            reverse('user_edit',
                    kwargs={'user_id': new_user.id}),
            {'username': 'rua_new_user',
             'first_name': 'changed',
             'last_name': 'changed',
             'middle_name': 'changed',
             'roles': '2',
             'country': 'GB',
             'email': 'fake_new_user@fakeaddress.com',
             'department': 'test',
             'signature': 'Hieee',
             'salutation': 'Mrs',
             'institution': 'rua_testing',
             'interests': 'gardening,ornithologyy,cats',
             'biography': 'bio'}
        )
        try:
            new_user = User.objects.get(username="rua_new_user")
            found = True
        except:
            found = False
        self.assertEqual(found, True)
        self.assertEqual(new_user.first_name, "changed")
        self.assertEqual(new_user.last_name, "changed")
        self.assertEqual(new_user.profile.middle_name, "changed")

    def test_manager_roles(self):
        resp = self.client.get(reverse('manager_roles'))
        roles = core_models.Role.objects.all()
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

        for role in roles:
            if not role.slug == 'press-editor':
                self.assertEqual(bytes(role.name, 'utf-8') in content, True)
                role_resp = self.client.get(reverse('manager_role', kwargs={
                    'slug': role.slug}))  # load role page
                role_content = role_resp.content
                self.assertEqual(role_resp.status_code, 200)
                self.assertNotIn(b"403", role_content)
                have_role = []
                dont_have_role = []
                users = User.objects.all()
                # get all users and see who has this role and who doesn't
                for user in users:
                    if user.profile.roles.filter(name=role.name).exists():
                        have_role.append(user)
                    else:
                        dont_have_role.append(user)
                # check for the users that have the role that a button exists
                # for removing the role
                for user in have_role:
                    remove_button = ('/manager/roles/{role_slug}/user/'
                                     '{user_id}/remove/'.format (
                        role_slug=role.slug,
                        user_id=user.id
                    ))
                    self.assertIn(bytes(remove_button, 'utf-8'), role_content)
                # check for the users that don't have the role that a button
                # exists for adding the role
                for user in dont_have_role:
                    add_button = (
                        f'/manager/roles/{role.slug}/user/{user.id}/add/'
                    )
                    self.assertIn(bytes(add_button, 'utf-8'), role_content)

                # either remove all users from a role or add them all
                expected_size = len(have_role) + len(dont_have_role)

                if len(have_role) > 0:
                    for user in have_role:
                        self.client.post(
                            reverse(
                                'manager_role_action',
                                kwargs={
                                    'slug': role.slug,
                                    'user_id': user.id,
                                    'action': 'remove'
                                }
                            )
                        )

                elif len(dont_have_role) > 0:
                    for user in dont_have_role:
                        self.client.post(
                            reverse(
                                'manager_role_action',
                                kwargs={
                                    'slug': role.slug,
                                    'user_id': user.id,
                                    'action': 'add'
                                }
                            )
                        )

                role_resp = self.client.get(
                    reverse(
                        'manager_role',
                        kwargs={'slug': role.slug}
                    )
                )
                role_content = role_resp.content
                self.assertEqual(role_resp.status_code, 200)
                have_role = []
                dont_have_role = []
                users = User.objects.all()

                # recreate lists
                for user in users:
                    if user.profile.roles.filter(name=role.name).exists():
                        have_role.append(user)
                    else:
                        dont_have_role.append(user)

                # check which list has all the users and check that the buttons
                # exist for removing or adding the roles
                if len(dont_have_role) > 0:
                    self.assertEqual(len(dont_have_role), expected_size)
                    for user in dont_have_role:
                        add_button = (
                            f'/manager/roles/{role.slug}/user/{user.id}/add/'
                        )
                        self.assertIn(bytes(add_button, 'utf-8'), role_content)
                else:
                    self.assertEqual(len(have_role), expected_size)
                    for user in have_role:
                        remove_button = (
                            f'/manager/roles/{role.slug}/user/{user.id}/remove/'
                        )
                        self.assertIn(
                            bytes(remove_button, 'utf-8'),
                            role_content
                        )

    def test_manager_groups(self):
        resp = self.client.get(reverse('manager_groups'))
        groups = models.Group.objects.all()
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        for group in groups:
            self.assertEqual(bytes(group.name, 'utf-8') in content, True)

        resp = self.client.post(
            reverse('manager_group_add'),
            {'group_type': 'generic',
             'name': 'rua_new_group',
             'active': True,
             'sequence': 4}
        )
        self.assertEqual(resp.status_code, 302)

        models.Group.objects.get(name="rua_new_group")
        resp = self.client.post(
            reverse('manager_group_edit',
                    kwargs={'group_id': 4}),
            {'group_type': 'generic',
             'name': 'changed_name',
             'active': True,
             'sequence': 4}
        )
        self.assertEqual(resp.status_code, 302)

        models.Group.objects.get(name="changed_name")
        resp = self.client.post(
            reverse('manager_group_delete',
                    kwargs={'group_id': 4})
        )
        self.assertEqual(resp.status_code, 302)
        matching_groups = models.Group.objects.filter(name="changed_name")
        self.assertEqual(matching_groups.count(), 0)

        editorial_group = models.Group.objects.get(name="rua_editorial_group")
        editorial_group_members = models.GroupMembership.objects.filter(
            group=editorial_group)
        self.assertEqual(len(editorial_group_members), 2)

        resp = self.client.get(
            reverse('manager_group_members',
           kwargs={'group_id': editorial_group.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        for member in editorial_group_members:
            self.assertIn(bytes(member.user.first_name, 'utf-8'), content)
            self.assertIn(bytes(member.user.last_name, 'utf-8'), content)
            remove_button = "/manager/groups/%s/members/%s/delete" % (
            editorial_group.id, member.id)
            self.assertIn(bytes(remove_button, 'utf-8'), content)

        resp = self.client.post(
            reverse(
                'manager_membership_delete',
                kwargs={
                    'group_id': editorial_group.id,
                    'member_id': 1
                }
            )
        )
        editorial_group_members = models.GroupMembership.objects.filter(
            group=editorial_group)
        self.assertEqual(len(editorial_group_members), 1)
        new_user = User.objects.get(username="rua_reviewer")

        resp = self.client.post(
            reverse(
                'group_members_assign',
                kwargs={
                    'group_id': editorial_group.id,
                    'user_id': new_user.id
                }
            )
        )
        editorial_group_members = models.GroupMembership.objects.filter(
            group=editorial_group)
        self.assertEqual(len(editorial_group_members), 2)

    def test_manager_settings(self):
        resp = self.client.get(reverse('settings_index'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(b"403" in content)
        groups = core_models.SettingGroup.objects.all()

        for group in groups:
            self.assertTrue(bytes(group.name.title(), 'utf-8') in content)
            settings = core_models.Setting.objects.filter(group=group)
            for setting in settings:
                self.assertIn(bytes(setting.name, 'utf-8'), content)
                setting_resp = self.client.get(
                    reverse(
                        'edit_setting',
                        kwargs={
                            'setting_group': group.name,
                            'setting_name': setting.name
                        }
                    )
                )
                self.assertEqual(setting_resp.status_code, 200)
                setting_content = setting_resp.content
                self.assertIn(b"Submit", setting_content)
                self.assertIn(b'name="value"', setting_content)
                self.assertIn(b"Delete", setting_content)

        setting = core_models.Setting.objects.get(
            name="remind_accepted_reviews"
        )
        self.assertEqual(setting.value, str(7))

        resp = self.client.post(
            reverse('edit_setting',
                     kwargs={'setting_group': 'cron',
                             'setting_name': setting.name}),
            {'value': 8}
        )
        self.assertEqual(resp.status_code, 302)
        setting.refresh_from_db()
        self.assertEqual(setting.value, str(8))


        resp = self.client.post(
            reverse('edit_setting',
                     kwargs={'setting_group': 'cron',
                             'setting_name': setting.name}),
            {'value': 8,
             'delete': 'delete'}
        )
        self.assertEqual(resp.status_code, 302)
        setting.refresh_from_db()
        self.assertEqual(setting.value, "")

    def test_manager_submission_checklist(self):
        resp = self.client.get(reverse('submission_checklist'))
        content = resp.content

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        self.assertEqual(b"Current Checklist Items" in content, True)
        self.assertEqual(b"Add new item" in content, True)
        items = submission_models.SubmissionChecklistItem.objects.all()
        self.assertEqual(len(items), 2)
        for item in items:
            list_item = "%s - %s" % (item.text, item.required)
            self.assertIn(bytes(list_item, 'utf-8'), content)

        self.client.post(
            reverse('submission_checklist'),
            {
                'slug': 'new_item',
                'text': 'item 3',
                'required': True,
                'sequence': 10
            }
        )
        items = submission_models.SubmissionChecklistItem.objects.all()
        self.assertEqual(len(items), 3)
        resp = self.client.get(reverse('submission_checklist'))
        content = resp.content
        for item in items:
            list_item = "%s - %s" % (item.text, item.required)
            self.assertIn(bytes(list_item, 'utf-8'), content)

        for item in items:
            resp = self.client.get(
                reverse(
                    'edit_submission_checklist',
                    kwargs={'item_id': item.id}
                )
            )
            content = resp.content

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(b"403" in content, False)

        self.client.post(
            reverse('edit_submission_checklist', kwargs={'item_id': 3}),
            {'slug': 'new_item', 'text': 'item 3', 'required': False,
             'sequence': 10})
        item = submission_models.SubmissionChecklistItem.objects.get(pk=3)
        self.assertEqual(item.required, False)
        resp = self.client.get(
            reverse('delete_submission_checklist', kwargs={'item_id': item.id}))
        items = submission_models.SubmissionChecklistItem.objects.all()
        self.assertEqual(len(items), 2)

    def test_manager_series(self):
        resp = self.client.get(reverse('series'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)
        series = core_models.Series.objects.all()
        self.assertEqual(series.count(), 0)

        resp = self.client.get(reverse('series_add'))
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

        resp = self.client.post(
            reverse('series_add'),
            {
                'title': 'test_series',
                'editor': 1,
                'issn': 'test issn',
                'description': 'test description',
                'url': 'http://localhost:8000/'
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(b"403" in resp.content, False)
        self.assertEqual(resp['Location'], '/manager/series/')

        all_series = core_models.Series.objects.all()
        self.assertEqual(all_series.count(), 1)

        resp = self.client.get(
            reverse('series_edit',
                    kwargs={'series_id': all_series.first().id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

        resp = self.client.post(
            reverse('series_edit',
                    kwargs={'series_id': all_series.first().id}),
            {
                'register': '',
                'title': 'test_series',
                'editor': '1',
                'issn': 'test issn',
                'description': 'test description updated',
                'url': 'http://localhost:8000/'
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(b"403", resp.content)
        self.assertEqual(resp['Location'], '/manager/series/')
        series = core_models.Series.objects.first()
        self.assertEqual(series.description, 'test description updated')

        resp = self.client.get(
            reverse('series_delete',
                    kwargs={'series_id': series.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

        book = core_models.Book.objects.first()

        resp = self.client.get(
            reverse('series_submission_add',
                    kwargs={'submission_id': book.id,
                            'series_id': series.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(b"403" in content, False)

        book.refresh_from_db()
        self.assertEqual(book.series, series)

        resp = self.client.get(
            reverse('series_submission_remove',
                    kwargs={'submission_id': book.id})
        )
        content = resp.content
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(b"403" in content, False)

        book.refresh_from_db()
        self.assertEqual(book.series, None)

        resp = self.client.post(
            reverse('series_delete',
                    kwargs={'series_id': series.id})
        )
        series = core_models.Series.objects.all()
        self.assertEqual(series.count(), 0)

    def test_manager_proposal_forms(self):
        resp = self.client.get(
            reverse(
                'manager_forms',
                kwargs={
                    'form_type': 'proposal'
                }
            )
        )
        content = resp.content
        proposal_forms = core_models.ProposalForm.objects.all()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"403" in content, False)

        for form in proposal_forms:
            self.assertEqual(bytes(form.name, 'utf-8') in content, True)
            view_button = "/manager/forms/proposal/{}/".format(form.id)
            self.assertIn(bytes(view_button, 'utf-8'), content)

            form_resp = self.client.get(
                reverse(
                    'manager_edit_form',
                    kwargs={
                        'form_type': 'proposal',
                        'form_id': form.id
                    }
                )
            )
            form_content = form_resp.content
            # Mirroring the logic in thFe view whereby a trying to edit a form
            # with in_edit set to false results in a redirect to 'manager_forms'
            if form.in_edit:
                self.assertEqual(form_resp.status_code, 200)
                self.assertTrue("Fields" in form_content)
                form_element_relationships = (
                    core_models.ProposalFormElementsRelationship.objects.filter(
                        form=form
                    )
                )
                self.assertEqual(len(form_element_relationships), 2)

                for field in form_element_relationships:
                    content_element = "<td>{}</td>".format(field.element.name)
                    self.assertTrue(content_element in form_content)
                    self.assertTrue(field.element.field_type in form_content)
                    delete_button = ('/manager/forms/proposal/{form_id}/'
                                     'element/{field_id}/delete/'.format(
                        form_id=form.id,
                        field_id=field.id
                    ))
                    self.assertEqual(delete_button in form_content, True)

            else:
                self.assertEqual(form_resp.status_code, 302)

            self.assertNotIn(b"403", form_content)

            self.client.get(
                reverse(
                    'manager_delete_form_element',
                    kwargs={
                        'form_type': 'proposal',
                        'form_id': form.id,
                        'relation_id': 1
                    }
                )
            )
            form_element_relationships = core_models.ProposalFormElementsRelationship.objects.filter(
                form=form
            )
            self.assertEqual(len(form_element_relationships), 1)

    def test_manager_form_creation(self):
        new_form_resp = self.client.post(
            reverse(
                'manager_add_new_form',
                kwargs={
                    'form_type': 'proposal'
                }
            ),
            {
                'name': 'new_test_form',
                'ref': 'test-new_form',
                'intro_text': 'introduction',
                'completion_text': 'completed'
            }
        )

        try:
            new_form = core_models.ProposalForm.objects.get(
                name='new_test_form'
            )
            found = True
        except ObjectDoesNotExist:
            found = False
        self.assertEqual(found, True)
        self.assertEqual(new_form_resp.status_code, 302)
        create_elements_url = '/manager/forms/proposal/'
        self.assertEqual(new_form_resp['Location'], create_elements_url)

    def test_form_elements(self):
        # Assuming the two form elements defined in the fixture
        # 'test/test_core_data' are present
        self.assertEqual(core_models.ProposalFormElement.objects.count(), 2)

        # Set form's 'in_edit' attribite to true to avoide redirect
        # in 'manager_edit_form' view
        form = core_models.ProposalForm.objects.get(pk=1)
        form.in_edit = True
        form.save()

        payload = {
            'name': 'new_test_element',
            'choices': '',
            'field_type': 'textarea',
            'order': 5,
            'required': False,
            'width': 'col-md-6',
            'help_text': ''
        }
        resp = self.client.post(
            reverse(
                'manager_edit_form',
                kwargs={
                    'form_type': 'proposal',
                    'form_id': 1
                }
            ),
            payload
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(core_models.ProposalFormElement.objects.count(), 3)

        payload = {
            'name': 'updated_new_test_element',
            'choices': '',
            'field_type': 'textarea',
            'order': 5,
            'required': False,
            'width': 'col-md-12',
            'help_text': 'updated'
        }
        self.client.post(
            reverse(
                'manager_edit_form_element',
                kwargs={
                    'form_type': 'proposal',
                    'form_id': 1,
                    'relation_id': 3
                }
            ),
            payload
        )
        form_elements = core_models.ProposalFormElement.objects.all()
        self.assertEqual(len(form_elements), 3)
        self.client.get(
            reverse(
                'manager_delete_form_element',
                kwargs={
                    'form_type': 'proposal',
                    'form_id': 1,
                    'relation_id': 3
                }
            )
        )
        form_elements = core_models.ProposalFormElement.objects.all()
        self.assertEqual(len(form_elements), 2)

    def test_manager_review_forms(self):
        resp = self.client.get(
            reverse(
                'manager_forms',
                kwargs={
                    'form_type': 'review'
                }
            )
        )
        content = resp.content
        review_forms = review_models.Form.objects.all()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b'403' in content, False)

        for form in review_forms:
            self.assertIn(bytes(form.name, 'utf-8'), content)
            view_button = '/manager/forms/review/{}/'.format(form.id)
            self.assertIn(bytes(view_button, 'utf-8'), content)
            form_resp = self.client.get(
                reverse(
                    'manager_edit_form',
                    kwargs={
                        'form_type': 'review',
                        'form_id': form.id
                    }
                )
            )
            form_content = form_resp.content

            # Mirroring logic in the manager_edit_form view which redirects
            # when 'in_edit' is not true for a given form
            if form.in_edit:
                self.assertEqual(form_resp.status_code, 200)
                self.assertIn(b"Fields", form_content)

                form_element_relationships = review_models.FormElementsRelationship.objects.filter(
                    form=form
                )
                self.assertEqual(len(form_element_relationships), 1)
                t = 0
                for field in form_element_relationships:
                    self.assertIn(
                        bytes(f'<td>{field.element.name}</td>', 'utf-8'),
                        form_content
                    )
                    self.assertIn(
                        bytes(field.element.field_type, 'utf-8'),
                        form_content
                    )
                    delete_button = (
                        '/manager/forms/review/{form_id}/element/'
                        '{field_id}/delete/'.format(
                            form_id=form.pk,
                            field_id=field.id
                        )
                    )
                    self.assertTrue(delete_button in form_content)
                    t += 1
                self.client.get(
                    reverse(
                        'manager_delete_form_element',
                        kwargs={
                            'form_type': 'review',
                            'form_id': form.id,
                            'relation_id':
                                review_models.FormElementsRelationship.objects.filter(
                                    form=form
                                )[0].pk
                        }
                    )
                )
                form_element_relationships = review_models.FormElementsRelationship.objects.filter(
                    form=form
                )
                self.assertEqual(len(form_element_relationships), 0)

            else:
                self.assertEqual(form_resp.status_code, 302)
            self.assertNotIn(b"403", form_content)

    def test_add_new_form(self):
        new_form_resp = self.client.post(
            reverse(
                'manager_add_new_form',
                kwargs={
                    'form_type': 'review'
                }
            ),
            {
                'name': 'new_test_form',
                'ref': 'test-new_form',
                'intro_text': 'introduction',
                'completion_text': 'completed',
                'in_edit': True,
            }
        )

        try:
            new_form = review_models.Form.objects.get(name='new_test_form')
            found = True
        except ObjectDoesNotExist:
            found = False

        self.assertEqual(found, True)
        self.assertEqual(new_form_resp.status_code, 302)
        create_elements_url = "/manager/forms/review/"
        self.assertEqual(new_form_resp['Location'], create_elements_url)

        # Ensure that there are no form elements in the db
        all_form_elements = review_models.FormElement.objects.all()
        for element in all_form_elements:
            element.delete()
        form_elements = review_models.FormElement.objects.all()
        self.assertEqual(len(form_elements), 0)

        resp = self.client.post(
            reverse(
                'manager_edit_form',
                kwargs={
                    'form_type': 'review',
                    'form_id': new_form.id
                }
            ),
            {
                'name': 'new_test_element',
                'choices': '',
                'field_type': 'textarea',
                'required': True,
                'order': 5,
                'width': 'col-md-6',
                'help_text': ''
            }
        )
        self.assertEqual(resp.status_code, 302)

        form_elements = review_models.FormElement.objects.all()
        self.assertEqual(len(form_elements), 1)
        self.client.get(
            reverse(
                'manager_delete_form_element',
                kwargs={
                    'form_type': 'review',
                    'form_id': new_form.id,
                    'relation_id': 2
                }
            )
        )
        form_elements = review_models.FormElement.objects.all()
        self.assertEqual(len(form_elements), 0)
