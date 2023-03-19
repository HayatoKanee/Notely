"""Tests of the delete notebook view"""
import json
import base64
from django.test import TestCase, RequestFactory
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Notebook, Folder
from django import forms
from notes.views import delete_notebook
from django.core.exceptions import PermissionDenied
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class DeleteNotebookViewTestCase(TestCase):
    """Tests for delete notebook view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
    
    def test_delete_notebook(self):
        request = self.factory.get(reverse('delete_notebook_tab', args=[self.notebook.id]))
        request.user = self.user
        response = delete_notebook(request, folder_id=self.notebook.folder.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('folders_tab'))
        self.assertFalse(Notebook.objects.filter(id=self.notebook.id).exists())

    def test_delete_notebook_unauthenticated(self):
        request = self.factory.get(reverse('delete_notebook_tab', args=[self.notebook.id]))
        request.user = self.user
        response = delete_notebook(request, folder_id=self.notebook.folder.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('folders_tab'))
        

    def test_delete_folder_permission_denied(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('delete_notebook_tab', args=[self.notebook.id])
        request = self.factory.get(url)
        request.user = other_user
        with self.assertRaises(PermissionDenied):
            response = delete_notebook(request, notebook_id=self.notebook.id)
        self.assertTrue(Notebook.objects.filter(id=self.notebook.id).exists())