from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from notes.helpers import calculate_age
from notes.models import User, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(pre_save, sender=Profile)
def save_age(sender, instance, **kwargs):
    # when date of birth is saved in the profile, calculate and save the age
    if instance.dob:
        instance.age = calculate_age(instance.dob)

