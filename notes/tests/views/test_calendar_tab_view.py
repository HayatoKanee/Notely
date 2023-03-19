"""Tests of the calendar tab view"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Permission
from notes.models import Event, User, EventTag
from notes.forms import EventForm, EventTagForm, ShareEventForm

class CalendarTabViewTestCase(TestCase):
    """Tests for calendar tab view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.tag = EventTag.objects.get(pk=1)
        self.event = Event.objects.get(pk=1)
        self.event.tags.add(self.tag)
        self.url = reverse('calendar_tab')
        self.client.login(username='johndoe', password='Password123')

    def test_calendar_tab_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_tab.html')
        self.assertIsInstance(response.context['event_form'], EventForm)
        self.assertIsInstance(response.context['tag_form'], EventTagForm)
        self.assertIsInstance(response.context['shareEvent_form'], ShareEventForm)
        self.assertIn(self.event, response.context['events'])
        self.assertIn(self.tag, response.context['tags'])

    def test_create_event(self):
        data = {
            'title': 'Test Event 2',
            'start_time': "2022-10-28 13:45:20 Z",
            'end_time': "2022-10-29 13:45:20 Z",
            'description': 'Test description 2',
            'tags': [self.tag.id],
            'page': ''
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Event.objects.last().title, 'Event2')

    def test_create_tag(self):
        self.tag2 = EventTag.objects.get(pk=2)
        data = {
            'tag': [self.tag2.id]
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EventTag.objects.count(), 2)
        self.assertEqual(EventTag.objects.last().title, 'work')

    def test_share_event(self):
        data = {
            'email': 'test@example.com',
            'message': 'Test message',
            'event': self.event.id
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_calendar_tab_view_creates_tag_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        tag_name = 'Test Tag'
        event= Event.objects.get(pk=2)
        response = self.client.post(reverse('calendar_tab'), {'tag_submit': '', 'title': tag_name})
        self.assertEqual(response.status_code, 302)

    def test_calendar_tab_view_creates_event_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        event= Event.objects.get(pk=2)
        response = self.client.post(reverse('calendar_tab'), {'event_submit': '', 'event': event})
        self.assertEqual(response.status_code, 200)

    def test_calendar_tab_view_share_event_on_form_submission(self):
        self.client.login(username='johndoe', password='Password123')
        event= Event.objects.get(pk=2)
        response = self.client.post(reverse('calendar_tab'), {'shareEvent_submit': ''})
        self.assertEqual(response.status_code, 200)

