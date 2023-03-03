"""Tests for event model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import EventTag


class EventModelTestCase(TestCase):
    """Tests for event model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.event_tag = EventTag.objects.get(pk=1)

    # Validation (helpers)
    def _assert_eventTag_is_valid(self):
        try:
            self.event.full_clean()
        except ValidationError:
            self.fail('Event should be valid')

    def _assert_eventTag_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.event.full_clean()
