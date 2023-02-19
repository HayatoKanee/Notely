from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from guardian.shortcuts import assign_perm

from notes.helpers import calculate_age
from notes.models import User, Profile, Notebook, Page


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


@receiver(post_save, sender=Page)
def give_permission(sender, instance, created, **kwargs):
    if created:
        assign_perm('dg_view_page', instance.notebook.user, instance)
        assign_perm('dg_edit_page', instance.notebook.user, instance)
        assign_perm('dg_delete_page', instance.notebook.user, instance)
