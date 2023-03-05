"""Unit tests for the page form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from notes.models import Notebook, User, PageTag, Page
from notes.forms import PageForm


class PageFormTestCase(TestCase):
    """Unit tests for the page form"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.page = Page.objects.get(pk=1)
        self.tag1 = PageTag.objects.get(pk=1)
        self.tag2 = PageTag.objects.get(pk=2)
        tag_queryset = PageTag.objects.all()
        self.form_data = {
            'tag': tag_queryset
        }

    def test_form_necessary_fields(self):
        form = PageForm()
        self.assertIn('tag', form.fields)

    def test_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['tag'] = self.tag2
        form = PageForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_save_page(self):
        form = PageForm(instance=self.page, data=self.form_data)
        self.assertTrue(form.is_valid())
        page = form.save()
        print(page)
        self.assertEqual(set(page.tags.all()), set(form.cleaned_data['tag']))
