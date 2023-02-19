from django.core.management.base import BaseCommand, CommandError
from notes.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):

        User.objects.filter(username='johndoe').delete()
        User.objects.filter(username='janedoe').delete()