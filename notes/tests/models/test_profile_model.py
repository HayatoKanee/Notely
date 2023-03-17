"""Tests for profile model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notes.models import Profile


class ProfileModelTestCase(TestCase):
    """Tests for Profile model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.profile = Profile.objects.get(id=1)

    def test_valid_profile(self):
        self._assert_profile_is_valid()

    # dob - test format
    def test_dob_is_valid(self):
        self.profile.dob = "1999-01-01"
        self._assert_profile_is_valid()

    def test_dob_is_invalid_format(self):
        self.profile.dob = "1999"
        self._assert_profile_is_invalid()

    def test_dob_is_in_the_future_is_invalid(self):
        self.profile.dob = "3000-01-01"
        self._assert_profile_is_invalid()

    def test_profile_must_have_user(self):
        self.profile.user = None
        self._assert_profile_is_invalid()

    # Validation (helpers)
    def _assert_profile_is_valid(self):
        try:
            self.profile.full_clean()
        except ValidationError:
            self.fail('Profile should be valid')

    def _assert_profile_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.profile.full_clean()
