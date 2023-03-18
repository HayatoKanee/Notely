"""Tests of the assign perm notebook view helper"""
from django.test import TestCase
from notes.models import Notebook, Page, Folder, User
from guardian.shortcuts import get_perms, get_users_with_perms
from view_helper import assign_perm_notebook

class AssignPermNotebookTestCase(TestCase):
    """Tests for assign perm notebook view helper"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.folder1 = Folder.objects.get(pk=1)
        self.notebook1 = Notebook.objects.get(pk=1)
        self.page1 = Page.objects.get(pk=1)

    def test_assign_perm_notebook_can_view_notebook(self):
        assign_perm_notebook(self.user2, self.notebook1)
        self.assertIn('dg_view_notebook', get_perms(self.user2, self.notebook1))
        
    def test_assign_perm_notebook_cannot_edit_notebook(self):
        assign_perm_notebook(self.user2, self.notebook1)
        self.assertNotIn('dg_edit_notebook', get_perms(self.user2, self.notebook1))
        
    def test_assign_perm_notebook_can_edit_notebook(self):
        assign_perm_notebook(self.user2, self.page1, can_edit=True)
        self.assertIn('dg_edit_notebook', get_perms(self.user2, self.notebook1))
         
    def test_assign_perm_notebook_can_view_folder(self):
        assign_perm_notebook(self.user2, self.notebook1)
        self.assertIn('dg_view_folder', get_perms(self.user2, self.folder1))
        
    def test_assign_perm_notebook_has_correct_users_with_perms(self):
        assign_perm_notebook(self.user2, self.notebook1)
        users_with_perms = get_users_with_perms(self.notebook1)
        self.assertIn(self.user2, users_with_perms)
        self.assertEqual(len(users_with_perms), 1)