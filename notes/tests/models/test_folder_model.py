"""Tests for folder model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import User, Folder


class ProfileModelTestCase(TestCase):
    """Tests for folder model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.folder = Folder.objects.get(pk=1)

    def test_valid_folder(self):
        self._assert_folder_is_valid()

    # name - test format
    def test_name_cannot_be_blank(self):
        self.folder.name = ''
        self._assert_folder_is_invalid()

    def test_name_can_be_10_characters_long(self):
        self.folder.name = 'x' * 10
        self._assert_folder_is_valid()

    def test_name_cannot_be_over_10_characters_long(self):
        self.folder.name = 'x' * 11
        self._assert_folder_is_invalid()

    def test_name_can_be_repeated_(self):
        self.folder.name = Folder.objects.get(pk=2).name
        self._assert_folder_is_valid()

    # Validation (helpers)
    def _assert_folder_is_valid(self):
        try:
            self.folder.full_clean()
        except ValidationError:
            self.fail('Profile should be valid')

    def _assert_folder_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.folder.full_clean()
