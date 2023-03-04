"""Unit tests for the event form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from notes.models import Event, User, Page, Tag, Reminder
from notes.forms import EventForm


class EventFormTestCase(TestCase):
    """Unit tests for the event form"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'title': 'SEG',
            'user': self.user,
            'description': 'meeting',
            'start_time': "2022-10-25 13:45:20 Z",
            'end_time': "2022-10-25 14:45:20 Z",
            'sync': True,
        }


    def test_valid_event_form(self):
        form = EventForm(data=self.form_input, user=self.user)
        self.assertTrue(form.is_valid())


    def test_form_necessary_fields(self):
        form = EventForm(user=self.user)
        self.assertIn('title', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('end_time', form.fields)


    def test_form_optional_fields(self):
        form = EventForm(user=self.user)
        self.assertIn('description', form.fields)
        self.assertIn('page', form.fields)
        self.assertIn('tag', form.fields)
        self.assertIn('reminder', form.fields)


    def test_form_invalid_with_end_time_before_start_time(self):
        self.form_input['start_time'] = "2022-10-25 14:45:20 Z"
        self.form_input['end_time'] = "2022-10-25 13:45:20 Z"
        form = EventForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('end_time', form.errors)
        self.assertEqual(form.errors['end_time'], ['End Time cannot be less that Start Time'])


    def test_form_invalid_with_missing_required_fields(self):
        form = EventForm(data={'user': self.user.id}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'], ['This field is required.'])
        self.assertIn('start_time', form.errors)
        self.assertEqual(form.errors['start_time'], ['This field is required.'])
        self.assertIn('end_time', form.errors)
        self.assertEqual(form.errors['end_time'], ['This field is required.'])


    