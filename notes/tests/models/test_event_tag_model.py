"""Tests for event model"""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from notes.models import EventTag, Event, User


class EventModelTestCase(TestCase):
    """Tests for event model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.event_tag = EventTag.objects.get(pk=1)

    def test_valid_tag(self):
        self._assert_eventTag_is_valid()

    def test_title_cannot_be_blank(self):
        self.event_tag.title = ''
        self._assert_eventTag_is_invalid()

    def test_title_can_be_30_characters_long(self):
        self.event_tag.title = 'x' * 30
        self._assert_eventTag_is_valid()

    def test_title_cannot_be_over_30_characters_long(self):
        self.event_tag.title = 'x' * 31
        self._assert_eventTag_is_invalid()

    def test_tag_colour_must_be_in_RGB_format(self):
        self.event_tag.color = "#F@1322"
        self._assert_eventTag_is_invalid()

    def test_event_tag_must_have_a_user(self):
        self.event_tag.user = None
        self._assert_eventTag_is_invalid()

    def test_event_tag_can_have_no_events(self):
        self.event_tag.events.all().delete()
        self._assert_eventTag_is_valid()

    def test_event_tag_can_have_more_than_one_event(self):
        event = Event.objects.create(title='My Event'
                                     , description='Event description',
                                     start_time=timezone.now(),
                                     end_time=timezone.now() + timedelta(minutes=20),
                                     user=User.objects.get(id=1)
                                     )
        self.event_tag.events.add(event)
        self._assert_eventTag_is_valid()

    # Validation (helpers)
    def _assert_eventTag_is_valid(self):
        try:
            self.event_tag.full_clean()
        except ValidationError:
            self.fail('EventTag should be valid')

    def _assert_eventTag_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.event_tag.full_clean()
