import json

from colorfield.fields import ColorField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from libgravatar import Gravatar
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from notes.helpers import validate_date
from notes.storage import CustomStorage


class User(AbstractUser):
    """User model used for authentication"""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\w{3}\w*$',
            message='Username must contain at least three alphanumericals and only alphanumericals'
        )]
    )
    email = models.EmailField(unique=True, blank=False)


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    age = models.IntegerField(
        unique=False,
        null=True,
        blank=True,
        validators=[MinValueValidator(limit_value=0, message="Age cannot be a negative number"),
                    MaxValueValidator(limit_value=180, message="Age is too high")]
    )
    dob = models.DateField(
        unique=False,
        null=True,
        blank=True,
        validators=[validate_date]
    )

    address = models.CharField(
        unique=False,
        max_length=200,
        validators=[RegexValidator(
            regex=r'^[\w|,|\s]*$',
            message='Address must only contain alphanuericals, spaces or commas'
        )],
        null=True,
        blank=True
    )

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.user.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=30)


class Folder(models.Model):
    user = models.ForeignKey(User, related_name="folders", on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name="sub_folders", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    folder_name = models.CharField(max_length=10)

    class Meta:
        permissions = [
            ("dg_view_folder", "can view folder"),
            ("dg_edit_folder", "can edit folder"),
            ("dg_delete_folder", "can delete folder")
        ]

    def get_type(self):
        return 'Folder'

    def get_path(self):
        path = [self]
        current = self.parent
        while current != None:
            path.insert(0, current)
            current = current.parent
        return path


class Notebook(models.Model):
    user = models.ForeignKey(User, related_name="notebooks", on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name="notebooks", on_delete=models.CASCADE, null=True, blank=True)
    notebook_name = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    last_page = models.OneToOneField('Page', related_name="last_page_of", on_delete=models.SET_NULL, null=True)

    class Meta:
        permissions = [
            ("dg_view_notebook", "can view notebook"),
            ("dg_edit_notebook", "can edit notebook"),
            ("dg_delete_notebook", "can delete notebook")
        ]

    def get_type(self):
        return 'Notebook'


class Page(models.Model):
    notebook = models.ForeignKey(Notebook, related_name="pages", on_delete=models.CASCADE)
    drawing = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='pages/thumbnails', storage=CustomStorage, blank=True)

    class Meta:
        permissions = [
            ("dg_view_page", "can view page"),
            ("dg_edit_page", "can edit page"),
            ("dg_delete_page", "can delete page")
        ]

    def delete(self, *args, **kwargs):
        try:
            notebook = self.last_page_of
            super().delete(*args, **kwargs)
            pages = notebook.pages.all()
            if pages.exists():
                notebook.last_page = pages.last()
                print(notebook.last_page)
            else:
                notebook.last_page = Page.objects.create(notebook=notebook)
            notebook.save()
        except ObjectDoesNotExist:
            super().delete(*args, **kwargs)

    def get_all_tags_id(self):
        ids = ""
        for tag in self.tags.all():
            ids += f'{tag.id},'
        if ids != "":
            return ids[:-1]
        return ids

    def get_page_number(self):
        """
        Returns the page number of this page within its respective notebook.
        """
        pages = self.notebook.pages.all()
        sorted_pages = sorted(pages, key=lambda p: p.id)
        index = sorted_pages.index(self)
        page_number = index + 1
        
        return page_number


class Editor(models.Model):
    title = models.CharField(max_length=10)
    code = models.TextField(blank=True)
    page = models.ForeignKey(Page, related_name="editors", on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        page = self.page
        super().delete(*args, **kwargs)
        editors = page.editors.all()
        if not editors.exists():
            Editor.objects.create(page=page)


class Tag(models.Model):
    title = models.CharField(max_length=30)
    COLOR_PALETTE = [
        ('#000000', 'Black'),
        ('#0000FF', 'Blue'),
        ('#C12FFF', 'Purple'),
        ('#34eb67', 'Green'),
        ('#FF5B09', 'Orange'),
        ('#FC1501', 'Red'),
        ('#FFFF00', 'Yellow'),
        ('#FFA3EE', 'Pink'),
    ]
    image = models.ImageField(upload_to="images")
    color = ColorField(image_field="image", samples=COLOR_PALETTE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class EventTag(Tag):
    user = models.ForeignKey(User, related_name="event_tags", on_delete=models.CASCADE)
    events = models.ManyToManyField('Event', related_name="tags", blank=True)


class PageTag(Tag):
    user = models.ForeignKey(User, related_name="page_tags", on_delete=models.CASCADE)
    pages = models.ManyToManyField(Page, related_name="tags", blank=True)


class Event(models.Model):
    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(default=" ")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    routine_choice = [
        ("0", "No Repeat"),
        ("1", "every Day"),
        ("2", "every Week"),
        ("3", "every 2 Weeks"),
        ("4", "every Month"),
        ("5", "every Year"),
        ("Custom", "Custom")
    ]
    week_choice = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]
    routine = models.CharField(choices=routine_choice, max_length=10, blank=True)
    google_id = models.CharField(blank=True, max_length=200)
    sync = models.BooleanField(blank=False, default=False)
    pages = models.ManyToManyField('Page', blank=True, related_name='events')

    class Meta:
        permissions = [
            ("dg_view_event", "can view event"),
            ("dg_edit_event", "can edit event"),
            ("dg_delete_event", "can delete event")
        ]


    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.sync:
            try:
                credential = Credential.objects.get(user=self.user)
            except Credential.DoesNotExist:
                return super().save()
            creds = Credentials.from_authorized_user_info(info=json.loads(credential.google_cred))
            # Create a service object to interact with the Google Calendar API
            service = build('calendar', 'v3', credentials=creds)
            g_event = {
                'summary': self.title,
                'description': self.description,
                'start': {
                    'dateTime': self.start_time.isoformat(),
                    'timeZone': self.start_time.strftime('%Z')
                },
                'end': {
                    'dateTime': self.end_time.isoformat(),
                    'timeZone': self.start_time.strftime('%Z')
                }
            }
            if self.google_id:
                try:
                    service.events().update(calendarId='primary', eventId=self.google_id, body=g_event).execute()
                except HttpError:
                    return super().save()
            else:
                created_event = service.events().insert(calendarId='primary', body=g_event).execute()
                self.google_id = created_event['id']
        super().save()

    def delete(self, using=None, keep_parents=False):
        if self.sync:
            try:
                credential = Credential.objects.get(user=self.user)
            except Credential.DoesNotExist:
                return super().delete(using=using, keep_parents=keep_parents)
            creds = Credentials.from_authorized_user_info(info=json.loads(credential.google_cred))
            # Create a service object to interact with the Google Calendar API
            service = build('calendar', 'v3', credentials=creds)
            if self.google_id:
                try:
                    service.events().delete(calendarId='primary', eventId=self.google_id).execute()
                except HttpError as error:
                    # Log error if the event was not found
                    if error.resp.status == 404:
                        print(f"Event with ID {self.google_id} not found.")
                    else:
                        raise
        super().delete(using=using, keep_parents=keep_parents)


class Reminder(models.Model):
    event = models.ForeignKey(Event, related_name="reminders", on_delete=models.CASCADE)
    reminder_choice = [
        (-1, "No reminder"),
        (0, "When event start"),
        (5, "5 minutes before"),
        (10, "10 minutes before"),
        (15, "15 minutes before"),
        (30, "30 minutes before"),
        (60, "1  hour before"),
        (120, "2  hours before"),
        (1440, "1  day before"),
        (2880, "2  days before"),
        (10080, "1  week before"),
    ]
    reminder_time = models.IntegerField(choices=reminder_choice)
    task_id = models.TextField(unique=True, blank=True, null=True)
    exact_time = models.DateTimeField(null=True)

class Credential(models.Model):
    user = models.ForeignKey(User, related_name="creds", on_delete=models.CASCADE)
    google_cred = models.TextField(blank=True)
