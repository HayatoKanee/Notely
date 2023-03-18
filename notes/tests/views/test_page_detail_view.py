"""Tests of the page detail view"""
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http import JsonResponse
from notes.models import Page, User
from notes.views import page_detail
from django.contrib.messages.api import MessageFailure


class PageDetailViewTestCase(TestCase):
    """Tests for page detail view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)

    def test_page_detail_view_GET(self):
        request = self.factory.get(reverse('page_detail', args=[self.page.id]))
        request.user = self.user
        response = page_detail(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

    def test_page_detail_view_POST(self):
        data = {"drawing": "Some other JSON data"}
        request = self.factory.post(reverse('page_detail', args=[self.page.id]), data=data)
        request.user = self.user
        with self.assertRaises(MessageFailure):
            response = page_detail(request, page_id=self.page.id)
        self.page.refresh_from_db()
        self.assertEqual(self.page.drawing, "Some JSON data")

    def test_get_page_detail_page(self):
        request = self.factory.get(reverse('page_detail', args=[self.page.id]))
        request.user = self.user
        response = page_detail(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 200)

    def test_get_page_detail_page_unauthenticated(self):
        request = self.factory.get(reverse('page_detail', args=[self.page.id]))
        request.user = self.user
        response = page_detail(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 200)

    def test_post_page_detail_page(self):
        request = self.factory.post(reverse('page_detail', args=[self.page.id]), data={'page_title': 'Updated Test Page', 'content': 'This is an updated test page'})
        request.user = self.user
        with self.assertRaises(MessageFailure):
            response = page_detail(request, page_id=self.page.id)
        updated_page = Page.objects.get(id=self.page.id)
        self.assertEqual(updated_page.drawing, 'Some JSON data')

    def test_post_page_detail_page_unauthenticated(self):
        request = self.factory.post(reverse('page_detail', args=[self.page.id]), data={'page_title': 'Updated Test Page', 'content': 'This is an updated test page'})
        request.user = self.user
        with self.assertRaises(MessageFailure):
            response = page_detail(request, page_id=self.page.id)
        updated_page = Page.objects.get(id=self.page.id)
        self.assertEqual(updated_page.drawing, 'Some JSON data')







