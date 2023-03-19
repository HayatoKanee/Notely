"""Tests of the confirm share folder view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import User, Page, Notebook, Folder

class ConfirmShareFolderViewTestCase(TestCase):
    """Tests for confirm share folder view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)
        

    def test_confirm_share_folder_with_valid_id_and_user(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('confirm_share_folder', kwargs={'folder_id': self.folder.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_confirm_share_folder_with_invalid_id(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('confirm_share_folder', kwargs={'folder_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_confirm_share_folder_with_unauthorized_user(self):
        unauthorized_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('confirm_share_folder', kwargs={'folder_id': self.folder.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

