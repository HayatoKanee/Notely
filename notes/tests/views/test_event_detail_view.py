"""Tests of the event detail view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from unittest.mock import patch
from notes.models import Event, Notebook, Page, Reminder, User
from notes.forms import EventForm
from datetime import datetime, timedelta, timezone


class EventDetailViewTestCase(TestCase):
    """Tests for event detail view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.other_user = User.objects.get(pk=2)
        self.event = Event.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)
        self.event.pages.add(self.page)
        self.client = Client()
        self.client.login(username='johndoe', password='Password123')

    def test_event_detail_view_with_valid_event_id(self):
        url = reverse('event_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/event_detail.html')

    def test_event_detail_view_with_invalid_event_id(self):
        url = reverse('event_detail', args=[999])  # Non-existent event id
        try:
            response = self.client.get(url)
        except:
            status = 1
        self.assertEqual(status, 1)

    def test_event_detail_view_with_valid_post_request(self):
        url = reverse('event_detail', args=[self.event.id])
        data = {
            'title': 'Event1',
            'description': 'some description',
            "start_time": "2022-10-25 13:45:20 Z",
            "end_time": "2022-10-27 13:45:20 Z",
            'pages': [self.page.id],
            'reminder': -1
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('calendar_tab'))
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Event1')
        self.assertEqual(self.event.description, 'some description')
        self.assertEqual(self.event.start_time, datetime(2022, 10, 25, 13, 45, 20, tzinfo=timezone.utc))
        self.assertEqual(self.event.end_time, datetime(2022, 10, 27, 13, 45, 20, tzinfo=timezone.utc))
        self.assertEqual(list(self.event.pages.all()), [self.page])
        self.assertTrue(self.event.reminders.exists())


    def test_event_detail_GET(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('event_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/event_detail.html')
        self.assertContains(response, 'Event1')
        self.assertContains(response, 'FC1')

    def test_event_detail_POST_valid_form(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('event_detail', args=[self.event.id])
        data = {
            'title': 'Updated Test Event',
            'start_time': "2022-10-28 13:45:20 Z",
            'end_time': "2022-10-29 13:45:20 Z",
            'pages': [self.page.id],
            'reminder': -1
        }
        response = self.client.post(url, data)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Event1")
        self.assertEqual(self.event.start_time, datetime(2022, 10, 25, 13, 45, 20, tzinfo=timezone.utc))
        self.assertEqual(self.event.end_time, datetime(2022, 10, 27, 13, 45, 20, tzinfo=timezone.utc))

    def test_event_detail_POST_invalid_form(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('event_detail', args=[self.event.id])
        data = {
            'title': '',
            "start_time": "2022-10-25 13:45:20 Z",
            "end_time": "2022-10-27 13:45:20 Z",
            'pages': [self.page.id],
            'reminder': -1
        }
        response = self.client.post(url, data)
        self.assertTemplateUsed(response, 'partials/event_detail.html')
        self.assertContains(response, 'This field is required')

    def test_event_detail_POST_permission_denied(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('event_detail', args=[self.event.id])
        data = {
            'title': 'Updated Test Event',
            'start_time': "2022-10-28 13:45:20 Z",
            'end_time': "2022-10-29 13:45:20 Z",
            'pages': [self.page.id],
            'reminder': -1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(title='Updated Test Event').exists())

    