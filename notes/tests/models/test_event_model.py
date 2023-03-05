"""Tests for event model"""
import json

from django.core.exceptions import ValidationError
from django.test import TestCase
from google.oauth2.credentials import Credentials
from google.rpc.http_pb2 import HttpResponse
from googleapiclient.errors import HttpError

import notes.models
from notes.models import User, Event, Credential
from unittest import mock


class EventModelTestCase(TestCase):
    """Tests for event model"""
    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.event = Event.objects.get(pk=1)

    def test_valid_event(self):
        self._assert_event_is_valid()

    # name - test format
    def test_name_cannot_be_blank(self):
        self.event.title = ''
        self._assert_event_is_invalid()

    def test_name_can_be_200_characters_long(self):
        self.event.title = 'x' * 200
        self._assert_event_is_valid()

    def test_name_cannot_be_over_200_characters_long(self):
        self.event.title = 'x' * 201
        self._assert_event_is_invalid()

    def test_name_can_be_repeated_(self):
        self.event.title = Event.objects.get(pk=2).title
        self._assert_event_is_valid()

    def test_save_if_sync_with_no_cred(self):
        self.event.description = "test"
        self.event.sync = True
        self.event.save()
        self.assertEqual(self.event.google_id, '')
        self.assertEqual(self.event.description, 'test')

    @mock.patch('notes.models.Credentials.from_authorized_user_info')
    @mock.patch('notes.models.build')
    def test_save_if_sync_with_cred_but_no_google_id(self, mock_build, mock_cred):
        mock_cred.return_value = 'test'
        mock_service = mock.Mock()
        mock_events = mock.Mock()
        mock_insert = mock.Mock()
        mock_insert.execute.return_value = {'id': 'test_id'}
        mock_events.insert.return_value = mock_insert
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        self.event.sync = True
        Credential.objects.create(user=self.event.user, google_cred='{"access_token": "test_token"}')
        self.event.save()
        self.assertEqual(self.event.google_id, 'test_id')

    @mock.patch('notes.models.Credentials.from_authorized_user_info')
    @mock.patch('notes.models.build')
    def test_save_if_sync_with_cred_and_google_id_but_may_not_be_the_owner(self, mock_build, mock_cred):
        mock_service = mock.Mock()
        mock_events = mock.Mock()
        mock_update = mock.Mock()
        mock_update.execute.side_effect = HttpError(resp=HttpResponse(reason='not owner'), content=b'Error')
        mock_events.update.return_value = mock_update
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        self.event.sync = True
        self.event.google_id = 'test_id'
        self.event.description = 'test'
        Credential.objects.create(user=self.event.user, google_cred='{"access_token": "test_token"}')
        self.event.save()
        self.event.refresh_from_db()
        self.assertNotEqual(self.event.description, 'test')

    @mock.patch('notes.models.Credentials.from_authorized_user_info')
    @mock.patch('notes.models.build')
    def test_save_if_sync_with_cred_and_google_id(self, mock_build, mock_cred):
        self.event.sync = True
        self.event.google_id = 'test_id'
        self.event.description = 'test'
        Credential.objects.create(user=self.event.user, google_cred='{"access_token": "test_token"}')
        self.event.save()
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'test')

    def test_delete_if_sync_with_no_cred(self):
        self.event.sync = True
        user = self.event.user
        before = user.events.count()
        self.event.delete()
        self.assertEqual(before - 1, user.events.count())

    @mock.patch('notes.models.Credentials.from_authorized_user_info')
    @mock.patch('notes.models.build')
    def test_delete_if_sync_with_cred_and_google_id(self, mock_build, mock_cred):
        self.event.sync = True
        self.event.google_id = 'test_id'
        Credential.objects.create(user=self.event.user, google_cred='{"access_token": "test_token"}')
        user = self.event.user
        before = user.events.count()
        self.event.delete()
        self.assertEqual(before - 1, user.events.count())

    @mock.patch('notes.models.Credentials.from_authorized_user_info')
    @mock.patch('notes.models.build')
    def test_delete_if_sync_with_cred_and_google_id_with_httperror(self, mock_build, mock_cred):
        mock_service = mock.Mock()
        mock_events = mock.Mock()
        mock_delete = mock.Mock()
        mock_delete.execute.side_effect = HttpError(resp=HttpResponse(reason='not owner'), content=b'Error')
        mock_events.delete.return_value = mock_delete
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        self.event.sync = True
        self.event.google_id = 'test_id'
        Credential.objects.create(user=self.event.user, google_cred='{"access_token": "test_token"}')
        user = self.event.user
        before = user.events.count()
        with self.assertRaises(HttpError):
            self.event.delete()
        self.assertEqual(before, user.events.count())

    @mock.patch('notes.models.Credentials.from_authorized_user_info')
    @mock.patch('notes.models.build')
    def test_delete_if_sync_with_cred_and_google_id_with_404error(self, mock_build, mock_cred):
        mock_service = mock.Mock()
        mock_events = mock.Mock()
        mock_delete = mock.Mock()
        mock_delete.execute.side_effect = HttpError(resp=HttpResponse(status=404, reason='not owner'), content=b'Error')
        mock_events.delete.return_value = mock_delete
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service
        self.event.sync = True
        self.event.google_id = 'test_id'
        Credential.objects.create(user=self.event.user, google_cred='{"access_token": "test_token"}')
        user = self.event.user
        before = user.events.count()
        with self.assertRaises(HttpError):
            self.event.delete()
        self.assertEqual(before, user.events.count())

    # Validation (helpers)
    def _assert_event_is_valid(self):
        try:
            self.event.full_clean()
        except ValidationError:
            self.fail('Event should be valid')

    def _assert_event_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.event.full_clean()
