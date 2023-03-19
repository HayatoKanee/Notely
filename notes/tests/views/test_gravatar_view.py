"""Tests of the gravatar view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

class GravatarViewTest(TestCase):
    """Tests for gravatar view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    
    def test_redirect_to_gravatar(self):
        """Test that gravatar view redirects to en.gravatar.com"""
        response = self.client.get(reverse('gravatar'))
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, "https://en.gravatar.com/")
        
    def test_gravatar_status_code(self):
        """Test that gravatar view returns 302 status code"""
        response = self.client.get(reverse('gravatar'))
        self.assertEqual(response.status_code, 302)
        
    def test_gravatar_response_content(self):
        """Test that gravatar view doesn't return any content"""
        response = self.client.get(reverse('gravatar'))
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content, b'')