"""Tests for folder model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import User, Folder


class FolderModelTestCase(TestCase):
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
        self.folder.folder_name = ''
        self._assert_folder_is_invalid()

    def test_name_can_be_10_characters_long(self):
        self.folder.folder_name = 'x' * 10
        self._assert_folder_is_valid()

    def test_name_cannot_be_over_10_characters_long(self):
        self.folder.folder_name = 'x' * 11
        self._assert_folder_is_invalid()

    def test_name_can_be_repeated_(self):
        self.folder.folder_name = Folder.objects.get(pk=2).folder_name
        self._assert_folder_is_valid()

    def test_folder_must_have_a_user(self):
        self.folder.user = None
        self._assert_folder_is_invalid()

    def test_folder_get_type(self):
        self.assertEqual(self.folder.get_type(), 'Folder')

    def test_folder_can_have_a_parent(self):
        parent = Folder.objects.create(user=User.objects.get(id=1),
                                       folder_name='my_folder')
        self.folder.parent = parent
        self._assert_folder_is_valid()

    def test_folder_can_have_no_parent(self):
        self.folder.parent = None
        self._assert_folder_is_valid()

    def test_folder_get_path(self):
        self.folder.parent = Folder.objects.create(user=User.objects.get(id=1),
                                                   folder_name='my_folder')
        path = self.folder.get_path()
        self.assertEqual(path[0], self.folder.parent)
        self.assertEqual(path[1], self.folder)

    # Validation (helpers)
    def _assert_folder_is_valid(self):
        try:
            self.folder.full_clean()
        except ValidationError:
            self.fail('Folder should be valid')

    def _assert_folder_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.folder.full_clean()
