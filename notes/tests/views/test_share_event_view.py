"""Tests of the share event view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from notes.models import User, Event
from unittest.mock import patch
from rest_framework.authtoken.models import Token
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from notes.models import Event
from notes.views import share_event


class ShareEventViewTestCase(TestCase):
    """Tests for share event view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            start_time=timezone.now(),
            end_time=timezone.now(),
            user=self.user,
        )

    def test_share_event_internal(self):
        url = reverse('share_event', args=[self.event.id])
        response = self.client.post(url, {'selected_users[]': [self.user.email]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('Test Event', response.json()['html'])

