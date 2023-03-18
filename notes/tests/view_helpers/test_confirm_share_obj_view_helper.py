"""Tests of the confirm share obj view helper"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_text
from guardian.shortcuts import assign_perm
from notes.models import Page, Notebook, Folder, Reminder, User
from notes.view_helper import confirm_share_obj

class ConfirmShareObjTestCase(TestCase):
    """Tests for confirm share obj view helper"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)

    def test_confirm_share_page_with_valid_request(self):
        assign_perm('dg_edit_page', self.user, self.page)
        notification = Reminder.objects.get(pk=1)
        url = reverse('confirm_share_page', args=[self.page.id])
        data = {
            'edit_perm': 'true'
        }
        self.client.force_login(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertTrue(self.user.has_perm('dg_view_page', self.page))
        self.assertTrue(self.user.has_perm('dg_edit_page', self.page))
        self.assertTrue(self.user.has_perm('dg_view_notebook', self.notebook))
        self.assertTrue(self.user.has_perm('dg_view_folder', self.folder))

    def test_confirm_share_notebook_with_valid_request(self):
        assign_perm('dg_edit_notebook', self.user, self.notebook)
        notification = Reminder.objects.create(
            recipient=self.user,
            verb='Share'
        )
        url = reverse('confirm_share_notebook', args=[self.notebook.id])
        data = {
            'edit_perm': 'true'
        }
        self.client.force_login(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertTrue(self.user.has_perm('dg_view_notebook', self.notebook))
        self.assertTrue(self.user.has_perm('dg_edit_notebook', self.notebook))
        self.assertTrue(self.user.has_perm('dg_view_folder', self.folder))

    def test_confirm_share_folder_with_valid_request(self):
        assign_perm('dg_edit_folder', self.user, self.folder)
        notification = Reminder.objects.create(
            recipient=self.user,
            verb='Share'
        )
        url = reverse('confirm_share_folder', args=[self.folder.id])
        data = {
            'edit_perm': 'true'
        }
        self.client.force_login(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertTrue(self.user.has_perm('dg_view_folder', self.folder))
        self.assertTrue(self.user.has_perm('dg_edit_folder', self.folder))

    def test_confirm_share_obj_with_invalid_request_method(self):
        url = reverse('confirm_share_page', args=[self.page.id])
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'fail', 'message': 'Invalid request method'})