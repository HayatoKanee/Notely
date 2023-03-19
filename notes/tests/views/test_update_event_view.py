"""Tests of the update event view"""
from django.test import TestCase, RequestFactory
from django.urls import reverse
from datetime import datetime, timezone
import json

from notes.models import Event, User
from notes.views import update_event


class UpdateEventTestCase(TestCase):
    """Tests for update event view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.event = Event.objects.get(pk=1)

    def test_update_event_authenticated(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.post(reverse('update_event', args=[self.event.id]), {
            'start': '2023-03-17T15:00:00.000Z',
            'end': '2023-03-17T17:00:00.000Z'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'success'})
        self.event.refresh_from_db()
        self.assertEqual(self.event.start_time, datetime(2023, 3, 17, 15, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(self.event.end_time, datetime(2023, 3, 17, 17, 0, 0, tzinfo=timezone.utc))

    def test_update_event_unauthenticated(self):
        response = self.client.post(reverse('update_event', args=[self.event.id]), {
            'start': '2023-03-17T15:00:00.000Z',
            'end': '2023-03-17T17:00:00.000Z'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('log_in') + '?next=' + reverse('update_event', args=[self.event.id]))

    def test_update_event_no_permission(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        response = self.client.post(reverse('update_event', args=[self.event.id]), {
            'start': '2023-03-17T15:00:00.000Z',
            'end': '2023-03-17T17:00:00.000Z'
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Event.objects.filter(start_time=datetime(2023, 3, 17, 15, 0, 0)).exists())
        self.assertFalse(Event.objects.filter(end_time=datetime(2023, 3, 17, 17, 0, 0)).exists())
        self.event.refresh_from_db()
        self.assertNotEqual(self.event.start_time, datetime(2023, 3, 17, 15, 0, 0))
        self.assertNotEqual(self.event.end_time, datetime(2023, 3, 17, 17, 0, 0))

    def test_update_event_invalid_request_method(self):
        request = self.factory.get(reverse('update_event', args=[self.event.id]))
        request.user = self.user
        response = update_event(request, event_id=self.event.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'fail')
        event = Event.objects.get(id=self.event.id)
        self.assertNotEqual(event.start_time.isoformat(), '2022-03-17T10:00:00+00:00')
        self.assertNotEqual(event.end_time.isoformat(), '2022-03-17T11:00:00+00:00')

        