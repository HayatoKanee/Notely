"""Tests for Page model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import Page


class NotebookModelTestCase(TestCase):
    """Tests for Page model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.page = Page.objects.get(pk=1)

    def test_valid_page(self):
        self._assert_page_is_valid()

    def test_notebook_cannot_be_none(self):
        self.page.notebook = None
        self._assert_page_is_invalid()

    def test_drawing_can_be_blank(self):
        self.page.drawing = ""
        self._assert_page_is_valid()

    # Validation (helpers)
    def _assert_page_is_valid(self):
        try:
            self.page.full_clean()
        except ValidationError:
            self.fail('Page should be valid')

    def _assert_page_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.page.full_clean()
