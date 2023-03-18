"""Tests of the share event view"""
from django.test import TestCase
from django.urls import reverse
from notes.models import User, Event
from unittest.mock import patch
from rest_framework.test import APIClient


from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from unittest.mock import patch

from notes.models import Event
from notes.views import share_event

class ShareEventViewTestCase(TestCase):
    """Tests for share event view"""

    fixtures = [
        'notes/tests/fixtures/default_user.json',
        'notes/tests/fixtures/other_users.json'
    ]


#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.get(pk=1)
#         self.event = Event.objects.get(pk=1)

#     def test_share_event_success(self):
#         self.client.login(username='johndoe', password='Password123')
#         url = reverse('share_event', args=[self.event.id])
#         response = self.client.post(url, {'email': 'janedoe@example.org'})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(Event.objects.count(), 2)
#         shared_event = Event.objects.first()
#         self.assertEqual(shared_event, self.event)
#         self.assertEqual(shared_event.user.email, 'johndoe@example.org')
#         self.assertEqual(response.json()['status'], 'success')

#     def test_share_event_fail_nonexistent_event(self):
#         self.client.login(username='johndoe', password='Password123')
#         url = reverse('share_event', args=[999])
#         response = self.client.post(url, {'email': 'janedoe@example.org'})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(Event.objects.count(), 2)
#         self.assertEqual(response.json()['status'], 'fail')

#     def test_share_event_fail_no_email_provided(self):
#         self.client.login(username='johndoe', password='Password123')
#         url = reverse('share_event', args=[self.event.id])
#         response = self.client.post(url, {})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(Event.objects.count(), 2)


# from django.test import TestCase, Client
# from django.urls import reverse
# from django.utils import timezone
# from rest_framework.authtoken.models import Token
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from unittest.mock import patch

# from notes.models import Event
# from notes.views import share_event


# class ShareEventViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
#         self.token = Token.objects.create(user=self.user)
#         self.client.login(username='testuser', password='testpass')
#         self.event = Event.objects.create(
#             title='Test Event',
#             description='Test event description',
#             start_time=timezone.now(),
#             end_time=timezone.now(),
#             user=self.user,
#         )

#     def test_share_event_internal(self):
#         url = reverse('share_event', args=[self.event.id])
#         response = self.client.post(url, {'selected_users[]': [self.user.email]})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['status'], 'success')
#         self.assertIn('Test Event', response.json()['html'])
#         self.assertIn('Test event description', response.json()['html'])

#     @patch.object(SendGridAPIClient, 'send')
#     def test_share_event_external(self, mock_send):
#         mock_send.return_value.status_code = 202
#         url = reverse('share_event', args=[self.event.id])
#         response = self.client.post(url, {'selected_users[]': ['test@example.com']})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['status'], 'fail')
#         self.assertIn('Event Shared!', str(response.content))
#         mock_send.assert_called_once()