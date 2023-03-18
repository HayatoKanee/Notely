"""Tests of the share folder view"""
from django.test import TestCase
from django.urls import reverse
from notes.models import User, Folder
from unittest.mock import patch
from rest_framework.test import APIClient

class ShareFolderViewTestCase(TestCase):
    """Tests for share folder view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)

    def test_share_folder_success(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('share_folder', args=[self.folder.id])
        response = self.client.post(url, {'email': 'janedoe@example.org'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Folder.objects.count(), 2)
        shared_folder = Folder.objects.first()
        self.assertEqual(shared_folder, self.folder)
        self.assertEqual(shared_folder.user.email, 'johndoe@example.org')
        self.assertEqual(response.json()['status'], 'success')

    def test_share_folder_fail_no_email_provided(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('share_folder', args=[self.folder.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Folder.objects.count(), 2)