from django.test import TestCase
from django.urls import reverse
from notes.tests.helpers_tests import reverse_with_next

class RedirectsTest(TestCase):
    def test_get_redirects_when_not_logged_in(self):
        self.url = reverse('folders_tab')
        redirect_url = reverse_with_next('log_in',self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302,target_status_code=200)
