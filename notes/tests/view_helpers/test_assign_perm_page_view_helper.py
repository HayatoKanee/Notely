"""Tests of the assign perm page view helper"""
from django.test import TestCase
from notes.models import Notebook, Page, Folder, User
from guardian.shortcuts import get_perms, get_users_with_perms
from view_helper import assign_perm_page

class AssignPermPageTestCase(TestCase):
    """Tests for assign perm page view helper"""

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

    def test_assign_perm_page_can_view_page(self):
        assign_perm_page(self.user2, self.page1)
        self.assertIn('dg_view_page', get_perms(self.user2, self.page1))
        
    def test_assign_perm_page_cannot_edit_page(self):
        assign_perm_page(self.user2, self.page1)
        self.assertNotIn('dg_edit_page', get_perms(self.user2, self.page1))
        
    def test_assign_perm_page_can_edit_page(self):
        assign_perm_page(self.user2, self.page1, can_edit=True)
        self.assertIn('dg_edit_page', get_perms(self.user2, self.page1))
        
    def test_assign_perm_page_can_view_notebook(self):
        assign_perm_page(self.user2, self.page1)
        self.assertIn('dg_view_notebook', get_perms(self.user2, self.page1.notebook))
        
    def test_assign_perm_page_can_view_folder(self):
        assign_perm_page(self.user2, self.page1)
        self.assertIn('dg_view_folder', get_perms(self.user2, self.folder1))
        
    def test_assign_perm_page_cannot_view_folder_without_permission(self):
        assign_perm_page(self.user2, self.page1)
        self.assertNotIn('dg_view_folder', get_perms(self.user1, self.folder1))
        
    def test_assign_perm_page_has_correct_users_with_perms(self):
        assign_perm_page(self.user2, self.page1)
        users_with_perms = get_users_with_perms(self.page1)
        self.assertIn(self.user2, users_with_perms)
        self.assertEqual(len(users_with_perms), 1)