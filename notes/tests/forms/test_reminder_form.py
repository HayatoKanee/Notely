"""Unit tests for the reminder form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from notes.models import Reminder, User, Event
from notes.forms import ReminderForm


class ReminderFormTestCase(TestCase):
    """Unit tests for the reminder form"""


    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.event = Event.objects.get(pk=1)
        self.form_input = {
            'event': self.event,
            'user': self.user.id,
            'reminder_time': 15
        }


    def test_reminder_form_valid(self):
        form = ReminderForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_necessary_fields(self):
        form = ReminderForm(user=self.user)
        self.assertIn('event', form.fields)
        self.assertIn('reminder_time', form.fields)


    def test_reminder_form_no_event(self):
        self.form_input['event'] = None
        form = ReminderForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_reminder_form_invalid_time(self):
        self.form_input['reminder_time'] = -10
        form = ReminderForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('reminder_time', form.errors)


    def test_reminder_form_empty(self):
        form = ReminderForm(user=self.user)
        self.assertFalse(form.is_valid())


    def test_reminder_form_with_other_user_event(self):
        event = Event.objects.exclude(user=self.user).first()
        form_input = {
            'event': event,
            'reminder_time': 15
        }
        form = ReminderForm(user=self.user, data=form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)


    def test_reminder_form_with_user_without_events(self):
        user = User.objects.get(username='janedoe')
        form = ReminderForm(user=user, data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)

        