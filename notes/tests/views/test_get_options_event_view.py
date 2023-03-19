"""Tests of the get options event view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import Event, User
from notes.views import get_options_event

class GetOptionsEventViewTestCase(TestCase):
    """Tests for get option event view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.event = Event.objects.get(pk=1)
        self.perm = Permission.objects.get(codename='dg_view_event')
        self.user.user_permissions.add(self.perm)
        self.client.login(username='johndoe', password='Password123')

    def test_get_options_event_returns_options(self):
        url = reverse('get_options_event', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('options', response.json())
        self.assertTrue(response.json()['options'])

    def test_get_options_event_returns_fail_for_nonexistent_event(self):
        url = reverse('get_options_event', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'fail')

