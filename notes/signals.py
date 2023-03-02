from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from guardian.shortcuts import assign_perm
from notes.helpers import calculate_age
from notes.models import User, Profile, Notebook, Page, Editor, Reminder, Event, Folder
from notes.tasks import send_notification
from django.core.mail import send_mail
from datetime import datetime, timedelta
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
        new_page = Page.objects.create(notebook=instance)
        instance.last_page = new_page
        instance.save()


@receiver(post_save, sender=Reminder)
def schedule_reminder(sender, instance, created, **kwargs):
    event_start_time = timezone.make_naive(instance.event.start_time)
    reminder_time = instance.reminder_time
    target_time = event_start_time - timedelta(minutes=reminder_time)
    if created:
        task = send_notification.apply_async(args=[instance.id], eta=target_time)
        instance.exact_time = target_time
        instance.task_id = task.id
        instance.save()


@receiver(post_save, sender=Page)
def create_editor(sender, instance, created, **kwargs):
    """Create an empty editor when user create a page"""
    if created:
        Editor.objects.create(page=instance, title="Editor1")


# @receiver(post_save, sender=Reminder)
# def send_reminder_email(sender, instance, created, **kwargs):
#     if not created:
#         # Check if reminder time is now
#         if instance.reminder_time == 0 or instance.event.start_time - timedelta(
#                 minutes=instance.reminder_time) <= datetime.now():
#             # Send email to event user's email
#             send_mail(
#                 f"Reminder for event: {instance.event.title}",
#                 instance.event.description,
#                 'winniethepooh.notely@gmail.com',
#                 [instance.event.user.email],
#                 fail_silently=False,
#             )


@receiver(post_save, sender=Page)
def give_perm_page(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_page', instance.notebook.user, instance)
        assign_perm('dg_edit_page', instance.notebook.user, instance)
        assign_perm('dg_delete_page', instance.notebook.user, instance)


@receiver(post_save, sender=Folder)
def give_perm_folder(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_folder', instance.user, instance)
        assign_perm('dg_edit_folder', instance.user, instance)
        assign_perm('dg_delete_folder', instance.user, instance)


@receiver(post_save, sender=Notebook)
def give_perm_notebook(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_notebook', instance.user, instance)
        assign_perm('dg_edit_notebook', instance.user, instance)
        assign_perm('dg_delete_notebook', instance.user, instance)

