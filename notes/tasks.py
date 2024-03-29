from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from guardian.shortcuts import get_users_with_perms

from notes.models import Reminder
from notes.consumer import ReminderConsumer
from datetime import datetime, timedelta
from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from notifications.signals import notify


async def send_to_group(group_name, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        group_name,
        {
            "type": "show_notification",
            "message": message
        },
    )


def send_internal_reminder(reminder, remind_time, recipient):
    notify.send(
        sender=reminder.event.user,
        recipient=recipient,
        verb='Reminder',
        actor="System",
        description=f"{reminder.event.title} will start at {remind_time}",
    )


def send_notification_email(reminder):
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
    users_with_perms = get_users_with_perms(reminder.event, only_with_perms_in=['dg_view_event'])
    for user in users_with_perms:
        email = user.email
        event = reminder.event
        title = event.title
        description = event.description
        start_time = event.start_time
        end_time = event.end_time

        subject = f"{title} will start {reminder_dict.get(reminder_time)} ."

        html_content = f'<p>{title} will start {reminder_dict.get(reminder_time)} .\n</p> <p>Please see below event details:\n</p> <p>description: {description}\n</p> <p>start time: {start_time}\n</p> <p>end time: {end_time}</p>'
        mail = Mail(
            from_email='winniethepooh.notely@gmail.com',
            to_emails=email,
            subject=subject,
            html_content=html_content)

        try:
            sg = SendGridAPIClient(
                api_key=settings.EMAIL_HOST_PASSWORD
            )
            response = sg.send(mail)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as ex:
            print("a")


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
    remind_text = reminder_dict.get(reminder_time)
    send_notification_email(reminder)
    users_with_perms = get_users_with_perms(reminder.event, only_with_perms_in=['dg_view_event'])
    send_internal_reminder(reminder, remind_text, users_with_perms)
    for user in users_with_perms:
        async_to_sync(send_to_group)(f"user_{user.id}",
                                     f"{reminder.event.title} will start {reminder_dict.get(reminder_time)} .")