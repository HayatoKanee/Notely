"""Tests of the delete event view"""
import json
import base64
from django.test import TestCase, RequestFactory
from django.urls import reverse
from notes.forms import LogInForm
from notes.models import User, Event
from django import forms
from notes.views import delete_event
from django.core.exceptions import PermissionDenied
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class DeleteEventViewTestCase(TestCase):
    """Tests for delete event view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.event = Event.objects.get(pk=1)
    
    def test_delete_event(self):
        request = self.factory.get(reverse('delete_event', args=[self.event.id]))
        request.user = self.user
        response = delete_event(request, event_id=self.event.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('calendar_tab'))
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_delete_event_unauthenticated(self):
        request = self.factory.get(reverse('delete_event', args=[self.event.id]))
        request.user = self.user
        response = delete_event(request, event_id=self.event.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('calendar_tab'))
        

    def test_delete_event_permission_denied(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('delete_event', args=[self.event.id])
        request = self.factory.get(url)
        request.user = other_user
        with self.assertRaises(PermissionDenied):
            response = delete_event(request, event_id=self.event.id)
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())