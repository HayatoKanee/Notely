from django.urls import path
from django.urls import re_path

from notes.consumer import ReminderConsumer, CanvasConsumer

websocket_urlpatterns = [
    path('ws/calendar', ReminderConsumer.as_asgi()),
    re_path(r'ws/page/(?P<page_id>\d+)/$', CanvasConsumer.as_asgi())
]