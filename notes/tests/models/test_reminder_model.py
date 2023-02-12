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

    # name - test format
    def test_name_cannot_be_blank(self):
        self.reminder.reminder_name = ''
        self._assert_reminder_is_invalid()

    def test_name_can_be_50_characters_long(self):
        self.reminder.reminder_name = 'x' * 50
        self._assert_reminder_is_valid()

    def test_name_cannot_be_over_50_characters_long(self):
        self.reminder.reminder_name = 'x' * 51
        self._assert_reminder_is_invalid()

    def test_name_can_be_repeated_(self):
        self.reminder.reminder_name = Reminder.objects.get(pk=2).reminder_name
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