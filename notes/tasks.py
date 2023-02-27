from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from notes.models import Reminder
from notes.consumer import ReminderConsumer
from datetime import datetime, timedelta
from celery import shared_task


async def send_to_group(group_name, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        group_name,
        {
            "type": "show_notification",
            "message": message
        },
    )


@shared_task
def send_notification(reminder_id):
    reminder = Reminder.objects.get(id=reminder_id)
    reminder_time = reminder.reminder_time
    reminder_dict = {
        0: "now",
        5: "in 5 minutes",
        10: "in 10 minutes",
        15: "in 15 minutes",
        30: "in 30 minutes",
        60: "in an hour",
        120: "in 2 hours",
        1440: "at tomorrow",
        2880: "at the day after tomorrow",
        10080: "at next week",
    }

    async_to_sync(send_to_group)(f"user_{reminder.event.user.id}",
                                 f"{reminder.event.title} will start {reminder_dict.get(reminder_time)} .")
