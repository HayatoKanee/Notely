"""Tests for PageTag model"""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from notes.models import PageTag, Page, Notebook


class PageTagModelTestCase(TestCase):
    """Tests for PageTag model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.page_tag = PageTag.objects.get(pk=1)

    def test_valid_tag(self):
        self._assert_pageTag_is_valid()

    def test_title_cannot_be_blank(self):
        self.page_tag.title = ''
        self._assert_pageTag_is_invalid()

    def test_title_can_be_30_characters_long(self):
        self.page_tag.title = 'x' * 30
        self._assert_pageTag_is_valid()

    def test_title_cannot_be_over_30_characters_long(self):
        self.page_tag.title = 'x' * 31
        self._assert_pageTag_is_invalid()

    def test_tag_colour_must_be_in_RGB_format(self):
        self.page_tag.color = "#F@1322"
        self._assert_pageTag_is_invalid()

    def test_page_tag_must_have_a_user(self):
        self.page_tag.user = None
        self._assert_pageTag_is_invalid()

    def test_page_tag_can_have_no_pages(self):
        self.page_tag.pages.all().delete()
        self._assert_pageTag_is_valid()

    def test_str_function(self):
        self.assertEqual(str(self.page_tag), 'FC')

    def test_page_tag_can_have_more_than_one_event(self):
        page = Page.objects.create(notebook=Notebook.objects.get(id=1))
        self.page_tag.pages.add(page)
        self._assert_pageTag_is_valid()

    # Validation (helpers)
    def _assert_pageTag_is_valid(self):
        try:
            self.page_tag.full_clean()
        except ValidationError:
            self.fail('PageTag should be valid')

    def _assert_pageTag_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.page_tag.full_clean()
