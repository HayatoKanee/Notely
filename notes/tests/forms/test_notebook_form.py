"""Unit tests for the notebook form"""
from django.core.exceptions import ValidationError
from django import forms
from django.test import TestCase
from notes.models import Notebook, User, Folder, Page
from notes.forms import NotebookForm


class NotebookFormTestCase(TestCase):
    """Unit tests for the notebook form"""


    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]


    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'notebook_name': 'notebook1',
            'user': self.user.id,
        }


    def test_valid_notebook_form(self):
        form = NotebookForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_necessary_fields(self):
        form = NotebookForm()
        self.assertIn('notebook_name', form.fields)


    def test_notebook_name_must_be_less_than_or_equal_to_10_character(self):
        self.form_input['notebook_name'] = 'notebook123'
        form = NotebookForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_can_be_saved_correctly(self):
        form = NotebookForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        page = Page.objects.get(pk=1)

        # save the form
        notebook = form.save(self.user)

        # check that the notebook was created correctly
        self.assertEqual(notebook.user, self.user)
        self.assertEqual(notebook.notebook_name, 'notebook1')
        self.assertIsNone(notebook.folder)
        self.assertEqual(notebook.last_page.id, 2)


    def test_notebook_name_cannot_be_blank(self):
        self.form_input['notebook_name'] = ''
        form = NotebookForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('notebook_name', form.errors)


    def test_notebook_with_same_name_and_user_cannot_be_created_twice(self):
        notebook = Notebook.objects.create(user=self.user, notebook_name='existing_notebook')
        self.form_input['notebook_name'] = 'existing_notebook'
        form = NotebookForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('notebook_name', form.errors)

    
    def test_notebook_folder_can_be_assigned(self):
        folder = Folder.objects.get(pk=1)
        self.form_input['notebook_name'] = 'notebook2'
        form = NotebookForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        # save the form
        notebook = form.save(self.user)
        notebook.folder = folder

        # check that the notebook was created correctly
        self.assertEqual(notebook.user, self.user)
        self.assertEqual(notebook.notebook_name, 'notebook2')
        self.assertEqual(notebook.folder, folder)
        self.assertEqual(notebook.get_type(), 'Notebook')
    
    def test_notebook_last_page_can_be_assigned(self):
        notebook = Notebook.objects.create(user=self.user, notebook_name='existing_notebook')
        page = Page.objects.get(pk=2)
        self.form_input['notebook_name'] = 'notebook3'
        self.form_input['last_page'] = page.id
        form = NotebookForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        # save the form
        notebook = form.save(self.user)

        # check that the notebook was created correctly
        self.assertEqual(notebook.user, self.user)
        self.assertEqual(notebook.notebook_name, 'notebook3')
        self.assertEqual(notebook.last_page.id, 3)
        self.assertEqual(notebook.get_type(), 'Notebook')