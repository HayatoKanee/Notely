from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from guardian.shortcuts import assign_perm
from notes.helpers import calculate_age
from notes.models import User, Profile, Notebook, Page, Editor , Reminder ,Event
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import datetime 
from django.utils import timezone

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(pre_save, sender=Profile)
def save_age(sender, instance, **kwargs):
    # when date of birth is saved in the profile, calculate and save the age
    if instance.dob:
        instance.age = calculate_age(instance.dob)


@receiver(post_save, sender=Notebook)
def create_page(sender, instance, created, **kwargs):
    if created:
        new_page = Page.objects.create(notebook=instance, last_page_of=instance)
        assign_perm('dg_view_page', instance.user, new_page)
        assign_perm('dg_edit_page', instance.user, new_page)
        assign_perm('dg_delete_page', instance.user, new_page)

@receiver(post_save, sender=Reminder)
def send_notification(sender, instance, **kwargs):
    # Get the notification time from the instance
    event_start_time = timezone.make_naive(instance.event.start_time)
    reminder_time = instance.reminder_time

    # Calculate the number of seconds until the reminder time
    now = datetime.datetime.now()
    user_time_zone = now.tzinfo
    seconds_until_reminder = (event_start_time - datetime.timedelta(minutes=int(reminder_time))) - now
    reminderDict = {
        "0": "now",
        "5": "in 5 minutes",
        "10": "in 10 minutes",
        "15": "in 15 minutes",
        "30": "in 30 minutes",
        "60": "in an hour",
        "120": "in 2 hours",
        "1440": "at tomorrow",
        "2880": "at the day after tomorrow",
        "10080": "at next week",
    }
    # If the notification time is in the future, schedule a message to be sent to the user's browser
    if seconds_until_reminder.total_seconds() > 0:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.event.user.id}",
            {
                "type": "schedule_reminder",
                "message": f"Reminder: {instance.event.title}  will start {reminderDict.get(instance.reminder_time)} .",
                "delay": seconds_until_reminder.total_seconds(),
            },
        )

@receiver(post_save, sender=Page)
def create_editor(sender, instance, created, **kwargs):
    """Create an empty editor when user create a page"""
    if created:
        Editor.objects.create(page=instance, title="Editor1")
