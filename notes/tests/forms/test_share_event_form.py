"""Unit tests for the share event form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from notes.models import User, Event
from notes.forms import ShareEventForm


class ShareEventFormTestCase(TestCase):
    """Unit tests for the share event form"""


    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.event = Event.objects.get(pk=1)
        self.form_data = {
            'event': self.event.id,
            'email': 'test@example.com',
            'message': 'This is a test message.'
        }
        

    def test_valid_form(self):
        form = ShareEventForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        

    def test_event_field_choices(self):
        form = ShareEventForm()
        event_choices = form.fields['event'].choices
        self.assertEqual(len(event_choices), Event.objects.count())
        self.assertIn((self.event.id, self.event.title), event_choices)
        

    def test_blank_form(self):
        form = ShareEventForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.cleaned_data.get('event'))
        self.assertEqual(form.cleaned_data.get('email'), '')
        self.assertEqual(form.cleaned_data.get('message'), '')
        

    def test_invalid_email(self):
        self.form_data['email'] = 'invalid-email'
        form = ShareEventForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        

    def test_event_field_required(self):
        self.form_data['event'] = None
        form = ShareEventForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)
        

    def test_message_field_optional(self):
        self.form_data['message'] = ''
        form = ShareEventForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['message'], '')
        

    def test_event_choice_not_valid(self):
        self.form_data['event'] = 1000  # an invalid event id
        form = ShareEventForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)
        

    def test_message_field_max_length(self):
        self.form_data['message'] = 'a' * 201
        form = ShareEventForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

        