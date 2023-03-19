"""Tests of the page view"""
from django.test import TestCase, Client
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Page,  PageTag, Notebook
from django.contrib.auth.models import Permission
from django import forms
from notes.forms import EventForm, EventTagForm, ShareEventForm
from django.core.exceptions import PermissionDenied
from unittest.mock import patch
from notes.tests.helpers_tests import LoginInTester, reverse_with_next
from notes.views import page


class PageViewTestCase(TestCase):
    """Tests for page view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)

        view_perm = Permission.objects.get(codename='dg_view_page')
        edit_perm = Permission.objects.get(codename='dg_edit_page')
        self.user.user_permissions.add(view_perm)
        self.user.user_permissions.add(edit_perm)

    def test_page_view_accessible_to_logged_in_user(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(reverse('page', args=[self.page.id]))
        self.assertEqual(response.status_code, 200)

    def test_page_view_redirects_to_login_for_anonymous_user(self):
        response = self.client.get(reverse('page', args=[self.page.id]))
        page_id = self.page.id
        self.assertRedirects(response, f'/log_in/?next=/page/{page_id}')

    def test_page_view_displays_page_title(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(reverse('page', args=[self.page.id]))
        self.assertContains(response, self.page.notebook.notebook_name)

    def test_page_view_creates_tag_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        tag_name = 'Test Tag'
        page= Page.objects.create(notebook_id=1)
        response = self.client.post(reverse('page', args=[page.id]), {'page_tag_submit': '', 'title': tag_name})
        self.assertEqual(response.status_code, 302)

    def test_page_view_creates_new_page_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.post(reverse('page', args=[self.page.id]), {'add_page_submit': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.notebook.pages.count(), 2)

    def test_page_view_search_page_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.post(reverse('page', args=[self.page.id]), {'search_page_submit': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.notebook.pages.count(), 1)

    def test_page_view_create_event_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.post(reverse('page', args=[self.page.id]), {'event_submit': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.notebook.pages.count(), 1)

    