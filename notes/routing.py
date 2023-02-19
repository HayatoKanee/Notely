from django.urls import path

from notes.consumer import ReminderConsumer

websocket_urlpatterns = [
    path('calendar_tab/', ReminderConsumer.as_asgi()),

]