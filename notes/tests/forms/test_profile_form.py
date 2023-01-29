"""Unit tests of the profile form"""
from django import forms
from django.test import TestCase
from notes.forms import UserForm, ProfileForm
from notes.models import User, Profile
from notes.helpers import calculate_age


class ProfileFormTestCase(TestCase):
    """Unit tests of the profile form"""

    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'dob': '10/05/2001',
            'address': '2 Regent Street, London, N1 0AE'
        }

    # Test that the form has all fields and of the correct data type
    def test_form_has_necessary_fields(self):
        form = ProfileForm()
        self.assertIn('dob', form.fields)
        self.assertIn('address', form.fields)
        date_field = form.fields['dob']
        self.assertTrue(isinstance(date_field, forms.DateField))
        date_widget = form.fields['dob'].widget
        self.assertTrue(isinstance(date_widget, forms.DateInput))

    # Test that form is valid
    def test_valid_profile_form(self):
        form = ProfileForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # Test that form uses validation from the Profile model
    def test_form_uses_model_validation(self):
        self.form_input['address'] = 'bad^address'
        form = ProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Test that form is saved with the correct information
    def test_form_must_save_correctly(self):
        user = User.objects.get(username='johndoe')
        form = ProfileForm(instance=user.profile, data=self.form_input)
        before_count = Profile.objects.count()
        form.save()
        after_count = Profile.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.profile.age, calculate_age(user.profile.dob))
        self.assertEqual(user.profile.address, '2 Regent Street, London, N1 0AE')
        self.assertEqual(user.profile.dob.year, 2001)
        self.assertEqual(user.profile.dob.month, 10)
        self.assertEqual(user.profile.dob.day, 5)
