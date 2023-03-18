"""Tests of the delete folder view"""
import json
import base64
from django.test import TestCase, RequestFactory
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Notebook, Folder
from django import forms
from notes.views import delete_folder
from django.core.exceptions import PermissionDenied
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class DeleteFolderViewTestCase(TestCase):
    """Tests for delete folder view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)
    
    def test_delete_folder(self):
        request = self.factory.get(reverse('delete_folder_tab', args=[self.folder.id]))
        request.user = self.user
        response = delete_folder(request, folder_id=self.folder.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('folders_tab'))
        self.assertFalse(Folder.objects.filter(id=self.folder.id).exists())

    def test_delete_folder_unauthenticated(self):
        request = self.factory.get(reverse('delete_folder_tab', args=[self.folder.id]))
        request.user = self.user
        response = delete_folder(request, folder_id=self.folder.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('folders_tab'))
        

    def test_delete_folder_permission_denied(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('delete_folder_tab', args=[self.folder.id])
        request = self.factory.get(url)
        request.user = other_user
        with self.assertRaises(PermissionDenied):
            response = delete_folder(request, folder_id=self.folder.id)
        self.assertTrue(Folder.objects.filter(id=self.folder.id).exists())

