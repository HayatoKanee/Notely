"""Tests of the save page view"""
import json
import base64
from django.test import TestCase, RequestFactory
from django.urls import reverse
from notes.forms import LogInForm
from django.core.files.base import ContentFile
from django.http import JsonResponse
from notes.models import User, Notebook, Page, Editor
from django import forms
from notes.forms import EventForm, EventTagForm, ShareEventForm
from notes.views import save_page
from notes.tests.helpers_tests import LoginInTester, reverse_with_next


class SavePageViewTestCase(TestCase):
    """Tests for save page view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.page = Page.objects.get(pk=1)
        self.notebook = Notebook.objects.get(pk=1)
        self.notebook.last_page = self.page
        self.notebook.save()
        self.user = User.objects.get(pk=1)
        self.client.login(username='johndoe', password='Password123')
    
    def test_save_page_not_post(self):
        request = RequestFactory().get('/save-page/')
        request.user = self.user
        response = save_page(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'fail')
    
    def test_save_page_success(self):
        request = RequestFactory().post('/save-page/')
        request.POST = {
            'canvas': 'canvas data',
            'editors': '[{"title": "editor 1", "code": "editor 1 code"}]',
            'thumbnail': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBx... (base64-encoded image data)'
        }
        request.user = self.user
        response = save_page(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
        new_page = Page.objects.get(id=self.page.id)
        self.assertEqual(new_page.drawing, 'canvas data')
        self.assertEqual(new_page.thumbnail.name, f'pages/thumbnails/{self.page.id}.jpeg')
        self.assertEqual(new_page.editors.count(), 1)
        new_editor = new_page.editors.first()
        self.assertEqual(new_editor.title, 'editor 1')
        self.assertEqual(new_editor.code, 'editor 1 code')

    def test_save_page_empty_editors(self):
        request = RequestFactory().post('/save-page/')
        request.POST = {
            'canvas': 'canvas data',
            'editors': '[]',
            'thumbnail': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBx... (base64-encoded image data)'
        }
        request.user = self.user
        response = save_page(request, page_id=self.page.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
        new_page = Page.objects.get(id=self.page.id)
        self.assertEqual(new_page.drawing, 'canvas data')
        self.assertEqual(new_page.thumbnail.url, '/media/pages/thumbnails/1.jpeg')