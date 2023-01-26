'''Tests of the home view'''
from django.test import TestCase
from django.urls import reverse
from notes.models import User

class HomeViewTestCase(TestCase):
    '''Tests of the home view'''

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.create_user(
            username='@johndoe',
            email='johndoe@example.org',
            password='Password123',
            is_active=True,
        )

    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home.html')

