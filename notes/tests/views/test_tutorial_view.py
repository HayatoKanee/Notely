"""Tests of the tutorial view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from notes.models import Folder, User
from notes.views import get_options_folder

class TutorialViewTestCase(TestCase):
    """Tests for tutorial view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_tutorial_view_rendered(self):
        """
        Test that the tutorial page is rendered correctly
        """
        response = self.client.get(reverse('tutorial'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutorial.html')

