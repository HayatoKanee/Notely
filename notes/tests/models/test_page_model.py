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

    def test_owner_get_all_permissions(self):
        owner = self.page.notebook.user
        self.assertTrue(owner.has_perms(
            ['dg_view_page',
             'dg_edit_page',
             'dg_delete_page'
             ]
            , self.page
        ))

    def test_delete_if_page_is_the_only_page(self):
        notebook = self.page.last_page_of
        before = notebook.pages.all().count()
        self.assertEqual(before, 1)
        self.page.delete()
        after = notebook.pages.all().count()
        self.assertEqual(before, after)
        self.assertNotEqual(notebook.last_page, None)

    def test_delete_if_page_is_not_the_only_page_but_the_last_page(self):
        notebook = self.page.last_page_of
        page = Page.objects.create(notebook=notebook)
        before = notebook.pages.all().count()
        self.assertEqual(before, 2)
        self.page.delete()
        after = notebook.pages.all().count()
        self.assertEqual(before - 1, after)
        self.assertEqual(notebook.last_page, page)

    def test_delete_if_page_is_not_the_only_page_also_not_the_last_page(self):
        notebook = self.page.notebook
        page = Page.objects.create(notebook=notebook)
        notebook.last_page = page
        before = notebook.pages.all().count()
        self.assertEqual(before, 2)
        self.page.delete()
        after = notebook.pages.all().count()
        self.assertEqual(before - 1, after)
        self.assertEqual(notebook.last_page, page)

    # Validation (helpers)
    def _assert_page_is_valid(self):
        try:
            self.page.full_clean()
        except ValidationError:
            self.fail('Page should be valid')

    def _assert_page_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.page.full_clean()
