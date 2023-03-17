"""Unit tests for the folder form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from notes.models import Folder, User
from notes.forms import FolderForm


class FolderFormTestCase(TestCase):
    """Unit tests for the folder form"""

    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'folder_name': 'folder1',
            'user': self.user.id,
        }

    def test_valid_folder_form(self):
        form = FolderForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_necessary_fields(self):
        form = FolderForm()
        self.assertIn('folder_name', form.fields)

    def test_folder_name_must_be_less_than_or_equal_to_10_character(self):
        self.form_input['folder_name'] = 'folder12345'
        form = FolderForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_can_be_saved_correctly(self):
        form = FolderForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        # save the form
        folder = form.save(self.user)

        # check that the folder was created correctly
        self.assertEqual(folder.user, self.user)
        self.assertEqual(folder.folder_name, 'folder1')
        self.assertIsNone(folder.parent)
        self.assertQuerysetEqual(
            folder.get_path(),
            [repr(folder)],
            transform=repr
    )

    def test_folder_name_cannot_be_blank(self):
        self.form_input['folder_name'] = ''
        form = FolderForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('folder_name', form.errors)

    def test_folder_with_same_name_and_user_cannot_be_created_twice(self):
        folder = Folder.objects.create(user=self.user, folder_name='existing_folder')
        self.form_input['folder_name'] = 'existing_folder'
        form = FolderForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('folder_name', form.errors)

    

   



