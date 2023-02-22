from django.urls import path

from notes.consumer import ReminderConsumer

websocket_urlpatterns = [
    path('ws/calendar', ReminderConsumer.as_asgi()),
]