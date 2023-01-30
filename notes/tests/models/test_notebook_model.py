"""Tests for NoteBook model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import User, Folder, Notebook


class NotebookModelTestCase(TestCase):
    """Tests for NoteBook model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.notebook = Notebook.objects.get(pk=1)

    def test_valid_notebook(self):
        self._assert_notebook_is_valid()

    # name - test format
    def test_name_cannot_be_blank(self):
        self.notebook.notebook_name = ''
        self._assert_notebook_is_invalid()

    def test_name_can_be_10_characters_long(self):
        self.notebook.notebook_name = 'x' * 10
        self._assert_notebook_is_valid()

    def test_name_cannot_be_over_10_characters_long(self):
        self.notebook.notebook_name = 'x' * 11
        self._assert_notebook_is_invalid()

    def test_name_can_be_repeated_(self):
        self.notebook.name = Notebook.objects.get(pk=2).notebook_name
        self._assert_notebook_is_valid()

    def test_folder_can_be_null(self):
        self.notebook.folder = None
        self._assert_notebook_is_valid()
    # Validation (helpers)

    def _assert_notebook_is_valid(self):
        try:
            self.notebook.full_clean()
        except ValidationError:
            self.fail('Notebook should be valid')

    def _assert_notebook_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.notebook.full_clean()
