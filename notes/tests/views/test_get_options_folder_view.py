"""Tests of the get options folder view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import Folder, User
from notes.views import get_options_folder

class GetOptionsFolderViewTestCase(TestCase):
    """Tests for get option folder view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)
        self.perm = Permission.objects.get(codename='dg_view_folder')
        self.user.user_permissions.add(self.perm)
        self.client.login(username='johndoe', password='Password123')

    def test_get_options_folder_returns_options(self):
        url = reverse('get_options_folder', args=[self.folder.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('options', response.json())
        self.assertTrue(response.json()['options'])

