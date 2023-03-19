from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from notes.models import Page, Template, User

class SaveTemplateTestCase(TestCase):
    """Tests for save template view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)
        self.template_content = 'Test Template Content'

    def test_save_template_with_valid_data(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('save_template', args=[self.page.id])
        response = self.client.post(url, {'template_content': self.template_content})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        template = Template.objects.filter(page=self.page).last()
        self.assertIsNotNone(template)
        self.assertEqual(template.content, self.template_content)

    def test_save_template_with_invalid_page_id(self):
        self.client.login(username='johndoe', password='Password123')
        url = reverse('save_template', args=[999])
        response = self.client.post(url, {'template_content': self.template_content})
        self.assertEqual(response.status_code, 404)
        template = Template.objects.filter(page=self.page).last()
        self.assertIsNone(template)

    def test_save_template_without_authentication(self):
        url = reverse('save_template', args=[self.page.id])
        response = self.client.post(url, {'template_content': self.template_content})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/log_in/?next=' + url)
        template = Template.objects.filter(page=self.page).last()
        self.assertIsNone(template)

    def test_save_template_without_permission(self):
        other_user = User.objects.get(pk=2)
        self.client.login(username='janedoe', password='Password123')
        url = reverse('save_template', args=[self.page.id])
        response = self.client.post(url, {'template_content': self.template_content})
        self.assertEqual(response.status_code, 403)
        template = Template.objects.filter(page=self.page).last()
        self.assertIsNone(template)