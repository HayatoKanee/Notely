from django.urls import path

from notes.consumer import ReminderConsumer

websocket_urlpatterns = [
    path('ws://localhost:8000/ws/calendar', ReminderConsumer.as_asgi()),

]