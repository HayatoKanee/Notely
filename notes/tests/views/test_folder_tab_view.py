"""Tests of the folder tab view"""
from django.test import TestCase
from django.contrib import messages
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Folder, Notebook
from django import forms
from notes.forms import FolderForm, NotebookForm
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class FolderTabViewTestCase(TestCase):
    """Tests for folder tab view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('folders_tab')
        self.user = User.objects.get(username='janedoe')
        self.user2 = User.objects.get(username='janedoe')
        self.form_input = {
            'user': self.user,
            'folder_name': 'testfolder',
        }
        self.notebook_form_input = {
            'user': self.user,
            'notebook_name': 'notebook',
        }

    def test_folders_tab_url(self):
        self.assertEqual(self.url, '/folders_tab/')

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

    def test_get_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_create_new_folder(self):
        self.client.login(username=self.user.email, password='Password123')
        folder_before = Folder.objects.count()
        data = self.form_input
        response = self.client.post(self.url, data, follow=True)
        folder_after = Folder.objects.count()
        self.assertEqual(folder_before + 1, folder_after)
        response_url = reverse('folders_tab')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'folders_tab.html')

    def test_folder_name_must_be_less_than_10_characters(self):
        self.client.login(username=self.user.email, password='Password123')
        self.false_form_input = {
            'user': self.user,
            'folder_name': 'test_folder',
        }
        form = FolderForm(data=self.false_form_input)
        self.assertFalse(form.is_valid())

    def test_create_new_notebook(self):
        self.client.login(username=self.user.email, password='Password123')
        notebook_before = Notebook.objects.count()
        data = self.notebook_form_input
        form = NotebookForm(data=data)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.url, data, follow=True)
        notebook_after = Notebook.objects.count()
        self.assertEqual(notebook_before + 1, notebook_after)
        response_url = reverse('folders_tab')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'folders_tab.html')

    def test_notebook_name_must_be_less_than_10_characters(self):
        self.client.login(username=self.user.email, password='Password123')
        self.false_notebook_form_input = {
            'user': self.user,
            'notebook_name': 'test_folder',
        }
        form = FolderForm(data=self.false_notebook_form_input)
        self.assertFalse(form.is_valid())

    def test_click_folder_leads_to_subfolder(self):
        self.client.login(username=self.user.email, password='Password123')
        folder = Folder.objects.get(user=self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    # def test_other_user_can_not_access_folder(self):
    #     self.client.login(username=self.user2.email, password='Password123')
    #     folder = Folder.objects.get(user=self.user)
    #     response = self.client.get(reverse('sub_folders_tab', args=[folder.id]))
    #     print(response)
