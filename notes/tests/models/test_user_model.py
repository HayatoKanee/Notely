"""Tests for user model"""
from django.test import TestCase
from notes.models import User
from django.core.exceptions import ValidationError


class UserModelTestCase(TestCase):
    """Tests for the user model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_cannot_be_less_than_3_characters_long(self):
        self.user.username = 'x' * 2
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = 'x' * 30
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user.username = 'x' * 31
        self._assert_user_is_invalid()

    def test_username_cannot_contain_non_alphanumericals(self):
        self.user.username = 'x' * 15 + '*' + '@'
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        otheruser = User.objects.get(username='janedoe')
        self.user.username = 'janedoe'
        self._assert_user_is_invalid()

    def test_username_must_contain_at_least_3_alphanumericals(self):
        self.user.username = 'jo'
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = 'j0hndoe2'
        self._assert_user_is_valid()

    def test_email_must_be_unique(self):
        otheruser = User.objects.get(username='janedoe')
        self.user.email = otheruser.email
        self._assert_user_is_invalid()

    def test_email_pattern_must_not_have_2_at(self):
        self.user.email = 'johndoe@exam@ple.org'
        self._assert_user_is_invalid()

    def test_email_pattern_must_have_a_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_pattern_may_have_2_dots(self):
        self.user.email = 'johndoe@example.ac.uk'
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()