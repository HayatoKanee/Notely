'''Unit tests for the User Model'''
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import User

# Create your tests here.
class UserModelTestCase(TestCase):
    '''Unit tests for the user model'''

    def setUp(self):
        self.user = User.objects.create_user(
            username='@janedoe',
            email='janedoe@example.org',
            password='Password123',
        )

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_not_repeat(self):
        second_user = self._create_second_user()
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    def test_username_may_contain_50_char(self):
        self.user.username = 'x' * 50
        self._assert_user_is_valid()

    def test_username_must_not_contain_more_than_50_char(self):
        self.user.username = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'janedoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'janedoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'janedoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'janedoe@@example.org'
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError) :
            self.fail('Test user should be valid.')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def _create_second_user(self):
        user = User.objects.create_user(
            username='@johndoe',
            email='johndoe@example.org',
            password='Password123',
        )
        return user

