"""Tests of the delete page view"""
import json
import base64
from django.test import TestCase, RequestFactory
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Notebook, Folder, Page
from django import forms
from notes.views import delete_page
from django.core.exceptions import PermissionDenied
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class DeletePageViewTestCase(TestCase):
    """Tests for delete page view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)
    
    def test_delete_page(self):
        request = self.factory.get(reverse('delete_page', args=[self.page.id]))
        request.user = self.user
        response = delete_page(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('page', args=[3]))
        self.assertFalse(Page.objects.filter(id=self.page.id).exists())

    def test_delete_page_unauthenticated(self):
        request = self.factory.get(reverse('delete_page', args=[self.page.id]))
        request.user = self.user
        response = delete_page(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('page', args=[3]))
        

    def test_delete_folder_permission_denied(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('delete_page', args=[self.page.id])
        request = self.factory.get(url)
        request.user = other_user
        with self.assertRaises(PermissionDenied):
            response = delete_page(request, page_id=self.page.id)
        self.assertTrue(Page.objects.filter(id=self.page.id).exists())