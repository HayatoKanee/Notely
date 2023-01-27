'''Tests of the home view'''
from django.test import TestCase
from django.urls import reverse
from notes.models import User


class HomeViewTestCase(TestCase):
    '''Tests of the home view'''

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@example.org',
            password='Password123',
            is_active=True,
        )

    def test_home_url(self):
        self.assertEqual(self.url, '/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirect_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('folders_tab')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'folders_tab.html')
