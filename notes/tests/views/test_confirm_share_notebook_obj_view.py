"""Tests of the confirm share notebook view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import User, Page, Notebook, Folder

class ConfirmShareNotebookViewTestCase(TestCase):
    """Tests for confirm share notebook view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
        

    def test_confirm_share_notebook_with_valid_id_and_user(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('confirm_share_notebook', kwargs={'notebook_id': self.notebook.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_confirm_share_notebook_with_invalid_id(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('confirm_share_notebook', kwargs={'notebook_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_confirm_share_notebook_with_unauthorized_user(self):
        unauthorized_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('confirm_share_notebook', kwargs={'notebook_id': self.notebook.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

