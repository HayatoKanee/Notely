"""Tests for event model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import Event, Reminder


class ReminderModelTestCase(TestCase):
    """Tests for reminder model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.reminder = Reminder.objects.get(pk=1)

    def test_valid_reminder(self):
        self._assert_reminder_is_valid()

    # Validation (helpers)
    def _assert_reminder_is_valid(self):
        try:
            self.reminder.full_clean()
        except ValidationError:
            self.fail('Reminder should be valid')

    def _assert_reminder_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.reminder.full_clean()
