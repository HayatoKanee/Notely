"""Tests of the share folder ex view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import Folder, User, Page, Notebook

class ShareFolderExViewTestCase(TestCase):
    """Tests for share folder ex view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.folder = Folder.objects.get(pk=1)
    
    def test_share_folder_ex_success(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('share_folder_ex', args=[self.folder.id])
        with self.assertRaises(ValueError):
            response = self.client.get(url)

    
    def test_share_folder_ex_failure(self):
        url = reverse('share_folder_ex', args=[self.folder.id])
        response = self.client.get(url)
        self.assertRedirects(
            response, f'/log_in/?next={url}', fetch_redirect_response=False
        )

