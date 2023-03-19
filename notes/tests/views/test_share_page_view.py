"""Tests of the share page view"""
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Page, User


class SharePageTestCase(TestCase):
    """Tests for share page view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)

    def test_share_page_with_valid_id(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(reverse('share_page', args=[self.page.id]))
        self.assertEqual(response.status_code, 200)

    def test_share_page_with_invalid_id(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(reverse('share_page', args=[999]))
        self.assertEqual(response.status_code, 200)

    def test_share_page_without_login(self):
        response = self.client.get(reverse('share_page', args=[self.page.id]))
        self.assertRedirects(response, f'/log_in/?next=/share_page/{self.page.id}')

    def test_share_page_post_request(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.post(reverse('share_page', args=[self.page.id]), {'email': 'test@example.com', 'message': 'Check out this page!'})
