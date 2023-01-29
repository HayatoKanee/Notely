"""Tests for profile view"""
from django.urls import reverse
from django.test import TestCase
from notes.models import User
from notes.tests.helpers_tests import reverse_with_next
from notes.forms import UserForm, ProfileForm
from django.contrib import messages
from notes.helpers import calculate_age


class ProfileViewTestCase(TestCase):
    """Tests for profile view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('profile_tab')
        self.user = User.objects.get(username='janedoe')
        self.profile = self.user.profile
        self.form_input = {
            'first_name': 'Jan2',
            'last_name': 'Doe2',
            'username': 'janedoe2',
            'email': 'janedoe2@example.org',
            'dob': '10/05/2001',
            'address': '241 Lion Street, London, S1 05C'
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile_tab/')

    def test_get_profile(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_tab.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        user_form = response.context['user_form']
        profile_form = response.context['profile_form']
        self.assertTrue(isinstance(user_form, UserForm))
        self.assertTrue(isinstance(profile_form, ProfileForm))
        self.assertEqual(user_form.instance, self.user)
        self.assertEqual(profile_form.instance, self.user.profile)

    def test_get_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_profile_update(self):
        self.client.login(username=self.user.email, password='Password123')
        self.form_input['username'] = 'BAD^USERNAME'
        self.form_input['dob'] = 'abc'
        before_count = User.objects.count()
        response = self.client.post(self.url, data=self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_tab.html')
        user_form = response.context['user_form']
        profile_form = response.context['profile_form']
        self.assertTrue(isinstance(user_form, UserForm))
        self.assertTrue(isinstance(profile_form, ProfileForm))
        self.assertTrue(user_form.is_bound)
        self.assertTrue(profile_form.is_bound)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.username, 'janedoe')
        self.assertEqual(self.user.email, 'janedoe@example.org')
        self.assertEqual(self.profile.age, calculate_age(self.user.profile.dob))
        self.assertEqual(self.profile.dob.year, 1999)
        self.assertEqual(self.profile.dob.month, 1)
        self.assertEqual(self.profile.dob.day, 1)
        self.assertEqual(self.profile.address, "2 Regent Street, London, N1 0AE")

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.user.email, password='Password123')
        self.form_input['username'] = 'johndoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_tab.html')
        user_form = response.context['user_form']
        profile_form = response.context['profile_form']
        self.assertTrue(isinstance(user_form, UserForm))
        self.assertTrue(isinstance(profile_form, ProfileForm))
        self.assertTrue(user_form.is_bound)
        self.assertTrue(profile_form.is_bound)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.username, 'janedoe')
        self.assertEqual(self.user.email, 'janedoe@example.org')
        self.assertEqual(self.profile.age, calculate_age(self.user.profile.dob))
        self.assertEqual(self.profile.dob.year, 1999)
        self.assertEqual(self.profile.dob.month, 1)
        self.assertEqual(self.profile.dob.day, 1)
        self.assertEqual(self.profile.address, "2 Regent Street, London, N1 0AE")

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_profile_update(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('profile_tab')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_tab.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.username, 'janedoe2')
        self.assertEqual(self.user.first_name, 'Jan2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'janedoe2@example.org')
        self.assertEqual(self.profile.age, calculate_age(self.user.profile.dob))
        self.assertEqual(self.profile.dob.year, 2001)
        self.assertEqual(self.profile.dob.month, 10)
        self.assertEqual(self.profile.dob.day, 5)
        self.assertEqual(self.profile.address, '241 Lion Street, London, S1 05C')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
