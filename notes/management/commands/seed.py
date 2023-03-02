from django.core.management.base import BaseCommand, CommandError
from notes.models import User
from faker import Faker
import django.db.utils

DEFAULT_PASSWORD = 'Password123'
USER_COUNT = 20


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user = User.objects.create_user(
            username='johndoe',
            email='john.doe@example.org',
            password=DEFAULT_PASSWORD
        )
        user = User.objects.create_user(
            username='janedoe',
            email='jane.doe@example.org',
            password=DEFAULT_PASSWORD
        )
        self.create_random_users()

    def create_random_users(self):
        count = 0
        while count < USER_COUNT:
            print(f'Seeding user {count}', end='\r')
            try:
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                user = User.objects.create_user(
                    username=f'{first_name}{last_name}',
                    email=f'{first_name}.{last_name}@example.org',
                    password=DEFAULT_PASSWORD
                )
            except django.db.utils.IntegrityError as e:
                continue
            count += 1
