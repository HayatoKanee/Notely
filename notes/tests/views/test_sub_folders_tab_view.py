"""Tests of the sub folder tab view"""
from django.test import TestCase
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Folder, Notebook
from django import forms
from notes.forms import FolderForm, NotebookForm
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class SubFolderTabViewTestCase(TestCase):
    """Tests for sub folder tab view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)
        self.folder.parent = None
        self.url = reverse('sub_folders_tab', args=[self.folder.id])
        self.folder2 = Folder.objects.get(pk=2)
        self.folder.parent = self.folder
        self.form_input = {
            'user': self.user,
            'folder_name': 'testfolder',
        }
        self.notebook_form_input = {
            'user': self.user,
            'notebook_name': 'notebook',
        }


    def test_sub_folders_tab_url(self):
        folder_id = self.folder.id
        self.assertEqual(self.url, f"/folders_tab/{folder_id}")

    def test_get_folders_notebooks(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'folders_tab.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        folders_form = response.context['folder_form']
        notebook_form = response.context['notebook_form']
        self.assertTrue(isinstance(folders_form, FolderForm))
        self.assertTrue(isinstance(notebook_form, NotebookForm))

    def test_logged_in_user_can_access_view(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(reverse('sub_folders_tab', args=[self.folder.id]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirected_to_login_page(self):
        response = self.client.get(reverse('sub_folders_tab', args=[self.folder.id]))
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('sub_folders_tab', args=[self.folder.id])}")

    def test_can_view_sub_folders_and_notebooks(self):
        child_folder = Folder.objects.get(pk=2)
        notebook = Notebook.objects.get(pk=1)
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(reverse('sub_folders_tab', args=[self.folder.id]))
        self.assertContains(response, child_folder.folder_name)
        self.assertContains(response, notebook.notebook_name)

    def test_can_create_new_folder(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.post(
            reverse('sub_folders_tab', args=[self.folder.id]),
            data={'folder_name': 'New Folder'},
            follow=True
        )
        self.assertContains(response, 'New Folder')

    def test_create_new_notebook(self):
        self.client.login(username=self.user.email, password='Password123')
        notebook_before = Notebook.objects.count()
        data = self.notebook_form_input
        form = NotebookForm(data=data)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.url, data, follow=True)
        notebook_after = Notebook.objects.count()
        self.assertEqual(notebook_before + 1, notebook_after)
        response_url = reverse('sub_folders_tab', args=[self.folder.id])
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'folders_tab.html')


    