from django.core.management.base import BaseCommand, CommandError
from notes.models import User

DEFAULT_PASSWORD = 'Password123'


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create_user(
            username='johndoe',
            email='john.doe@example.org',
            password=DEFAULT_PASSWORD
        )
