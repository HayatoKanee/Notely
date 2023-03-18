"""Tests of the share notebook view"""
from django.test import TestCase
from django.urls import reverse
from notes.models import Notebook, User, Folder
from unittest.mock import patch
from rest_framework.test import APIClient

class ShareNotebookViewTestCase(TestCase):
    """Tests for share notebook view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)

    def test_share_notebook_success(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('share_notebook', args=[self.notebook.id])
        response = self.client.post(url, {'email': 'janedoe@example.org'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notebook.objects.count(), 2)
        shared_notebook = Notebook.objects.first()
        self.assertEqual(shared_notebook, self.notebook)
        self.assertEqual(shared_notebook.user.email, 'johndoe@example.org')
        self.assertEqual(response.json()['status'], 'success')

    def test_share_notebook_fail_nonexistent_notebook(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('share_notebook', args=[999])
        response = self.client.post(url, {'email': 'janedoe@example.org'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notebook.objects.count(), 2)
        self.assertEqual(response.json()['status'], 'fail')

    def test_share_notebook_fail_no_email_provided(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('share_notebook', args=[self.notebook.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notebook.objects.count(), 2)