"""Tests for editor model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import Editor, Page


class ReminderModelTestCase(TestCase):
    """Tests for editor model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.editor = Editor.objects.get(pk=1)

    def test_valid_editor(self):
        self._assert_editor_is_valid()

    def test_name_cannot_be_blank(self):
        self.editor.title = ''
        self._assert_editor_is_invalid()

    def test_name_can_be_10_characters_long(self):
        self.editor.title = 'x' * 10
        self._assert_editor_is_valid()

    def test_name_cannot_be_over_10_characters_long(self):
        self.editor.title = 'x' * 11
        self._assert_editor_is_invalid()

    def test_name_can_be_repeated_(self):
        self.editor.title = Editor.objects.create(
            title='editorX',
            page=Page.objects.get(pk=1)
        ).title
        self._assert_editor_is_valid()

    def test_code_can_be_empty_(self):
        self.editor.code = ""
        self._assert_editor_is_valid()

    def test_editor_must_have_a_page(self):
        self.editor.page = None
        self._assert_editor_is_invalid()

    def test_page_must_have_at_least_one_editor(self):
        self.assertEqual(self.editor.page.editors.count(), 1)
        self.editor.delete()
        self.assertEqual(self.editor.page.editors.count(), 1)

    # Validation (helpers)
    def _assert_editor_is_valid(self):
        try:
            self.editor.full_clean()
        except ValidationError:
            self.fail('Editor should be valid')

    def _assert_editor_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.editor.full_clean()
