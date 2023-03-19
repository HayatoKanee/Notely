"""Unit tests for the event form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from notes.models import Event, User, EventTag, Page
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
        self.tag1 = EventTag.objects.get(pk=1)
        self.tag2 = EventTag.objects.get(pk=2)
        self.page = Page.objects.get(pk=1)

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

    def test_save_the_event(self):
        form = EventForm(self.user, data=self.form_input)
        self.assertTrue(form.is_valid())
        event = form.save()
        self.assertEqual(event.title, form.cleaned_data['title'])
        self.assertEqual(event.description, form.cleaned_data['description'])
        self.assertEqual(event.start_time, form.cleaned_data['start_time'])
        self.assertEqual(event.end_time, form.cleaned_data['end_time'])
        self.assertEqual(event.user, self.user)

    def test_save_with_tag(self):
        form_data = self.form_input.copy()
        form_data['tag'] = [self.tag1]
        form = EventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        event = form.save()
        self.assertEqual(event.user, self.user)
        self.assertEqual(set(event.tags.all()), set(form.cleaned_data['tag']))

    def test_save_event_with_page(self):
        form_data = self.form_input.copy()
        form_data['page'] = self.page
        form = EventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        event = form.save()
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.pages.count(), 1)
        self.assertEqual(event.pages.first(), self.page)