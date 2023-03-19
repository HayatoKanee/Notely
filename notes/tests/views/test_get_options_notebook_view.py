"""Tests of the get options notebook view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import Notebook, User
from notes.views import get_options_notebook

class GetOptionsNotebookViewTestCase(TestCase):
    """Tests for get option notebook view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
        self.perm = Permission.objects.get(codename='dg_view_notebook')
        self.user.user_permissions.add(self.perm)
        self.client.login(username='johndoe', password='Password123')

    def test_get_options_notebook_returns_options(self):
        url = reverse('get_options_notebook', args=[self.notebook.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('options', response.json())
        self.assertTrue(response.json()['options'])

    def test_get_options_notebook_returns_fail_for_nonexistent_notebook(self):
        url = reverse('get_options_notebook', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'fail')

