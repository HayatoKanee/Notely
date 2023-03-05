"""Tests for event model"""
import json

from django.core.exceptions import ValidationError
from django.test import TestCase
from google.oauth2.credentials import Credentials

from notes.models import User, Event, Credential
from unittest import mock


class EventModelTestCase(TestCase):
    """Tests for event model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.event = Event.objects.get(pk=1)

    def test_valid_event(self):
        self._assert_event_is_valid()

    # name - test format
    def test_name_cannot_be_blank(self):
        self.event.title = ''
        self._assert_event_is_invalid()

    def test_name_can_be_200_characters_long(self):
        self.event.title = 'x' * 200
        self._assert_event_is_valid()

    def test_name_cannot_be_over_200_characters_long(self):
        self.event.title = 'x' * 201
        self._assert_event_is_invalid()

    def test_name_can_be_repeated_(self):
        self.event.title = Event.objects.get(pk=2).title
        self._assert_event_is_valid()

    def test_save_if_sync_with_no_cred(self):
        self.event.description = "test"
        self.event.sync = True
        self.event.save()
        self.assertEqual(self.event.google_id, '')
        self.assertEqual(self.event.description, 'test')

    # Validation (helpers)
    def _assert_event_is_valid(self):
        try:
            self.event.full_clean()
        except ValidationError:
            self.fail('Event should be valid')

    def _assert_event_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.event.full_clean()
