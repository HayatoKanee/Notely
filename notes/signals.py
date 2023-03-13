from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from guardian.shortcuts import assign_perm, get_users_with_perms
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


@receiver(post_save, sender=Reminder)
def schedule_reminder(sender, instance, created, **kwargs):
    event_start_time = timezone.localtime(instance.event.start_time)
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
        viewable_users = get_users_with_perms(instance.notebook, only_with_perms_in=['dg_view_all_notebook'])
        editable_users = get_users_with_perms(instance.notebook, only_with_perms_in=['dg_edit_all_notebook'])
        assign_perm('dg_view_page', instance.notebook.user, instance)
        for user in viewable_users:
            assign_perm('dg_view_page', user, instance)
        assign_perm('dg_edit_page', instance.notebook.user, instance)
        for user in editable_users:
            assign_perm('dg_edit_page', user, instance)
        assign_perm('dg_delete_page', instance.notebook.user, instance)


@receiver(post_save, sender=Folder)
def give_perm_folder(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_folder', instance.user, instance)
        assign_perm('dg_edit_folder', instance.user, instance)
        assign_perm('dg_delete_folder', instance.user, instance)
        assign_perm('dg_view_all_folder', instance.user, instance)
        assign_perm('dg_edit_all_folder', instance.user, instance)
        if instance.parent:
            viewable_users = get_users_with_perms(instance.parent, only_with_perms_in=['dg_view_all_folder'])
            editable_users = get_users_with_perms(instance.parent, only_with_perms_in=['dg_edit_all_folder'])
            for user in viewable_users:
                assign_perm('dg_view_folder', user, instance)
                assign_perm('dg_view_all_folder', user, instance)
            for user in editable_users:
                assign_perm('dg_edit_folder', user, instance)
                assign_perm('dg_edit_all_folder', user, instance)


@receiver(post_save, sender=Notebook)
def give_perm_notebook(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_notebook', instance.user, instance)
        assign_perm('dg_edit_notebook', instance.user, instance)
        assign_perm('dg_delete_notebook', instance.user, instance)
        assign_perm('dg_view_all_notebook', instance.user, instance)
        assign_perm('dg_edit_all_notebook', instance.user, instance)
        if instance.folder:
            viewable_users = get_users_with_perms(instance.folder, only_with_perms_in=['dg_view_all_folder'])
            editable_users = get_users_with_perms(instance.folder, only_with_perms_in=['dg_edit_all_folder'])
            for user in viewable_users:
                assign_perm('dg_view_notebook', user, instance)
                assign_perm('dg_view_all_notebook', user, instance)
            for user in editable_users:
                assign_perm('dg_edit_notebook', user, instance)
                assign_perm('dg_edit_all_notebook', user, instance)
        new_page = Page.objects.create(notebook=instance)
        instance.last_page = new_page
        instance.save()


@receiver(post_save, sender=Event)
def give_perm_event(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_event', instance.user, instance)
        assign_perm('dg_edit_event', instance.user, instance)
        assign_perm('dg_delete_event', instance.user, instance)
