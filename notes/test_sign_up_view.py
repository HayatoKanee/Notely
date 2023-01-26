'''Tests of the sign up view'''
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from notes.forms import SignUpForm
from notes.models import User
from .helpers_tests import LoginInTester


class SignUpViewTestCase(TestCase, LoginInTester):
    '''Tests of the sign up view'''

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'username': '@janedoe',
            'email': 'jane.doe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
        }
        self.user = User.objects.create_user(
            username='@johndoe',
            email='johndoe@example.org',
            password='Password123',
            is_active=True,
        )

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_sign_up_redirects_when_logged_in(self):
        self.client.login(username='@johndoe',password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('folders_tab')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'folders_tab.html')

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'BAD_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('folders_tab')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'folders_tab.html')
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.email, 'jane.doe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_post_sign_up_redirects_when_logged_in(self):
        self.client.login(username='@johndoe',password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('folders_tab')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'folders_tab.html')
