from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from libgravatar import Gravatar
from datetime import datetime
from django.urls import reverse

from notes.helpers import validate_date


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
    last_page_of = models.OneToOneField(Notebook, related_name="last_page", on_delete=models.CASCADE, null=True,
                                        blank=True)

    class Meta:
        permissions = [
            ("dg_view_page", "can view page"),
            ("dg_edit_page", "can edit page"),
            ("dg_delete_page", "can delete page")
        ]

    def delete(self, *args, **kwargs):
        notebook = self.last_page_of
        super().delete(*args, **kwargs)
        pages = notebook.pages.all()
        if pages.exists():
            notebook.last_page = pages.last()
        else:
            notebook.last_page = Page.objects.create(notebook=notebook, last_page_of=notebook)


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
    title = models.CharField(max_length=30, unique=True)
    COLOR_PALETTE = [
        ('#000000', 'black'),
        ('#0000FF', 'Blue'),
        ('#C12FFF', 'Purple'),
        ('#34eb67', 'green'),
        ('#FF5B09', 'orange'),
        ('#FC1501', 'red'),
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
    description = models.TextField(default="")
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

class GoogleEvent(Event):
    google_id = models.CharField(blank=False, max_length=200)
    sync = models.BooleanField(default=False)

    

class Reminder(models.Model):
    event = models.ForeignKey(Event, related_name="reminders", on_delete=models.CASCADE)
    reminder_choice = [
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


class Credential(models.Model):
    user = models.ForeignKey(User, related_name="creds", on_delete=models.CASCADE)
    google_cred = models.TextField(blank=True)


class Credential(models.Model):
    user = models.ForeignKey(User, related_name="creds", on_delete=models.CASCADE)
    google_cred = models.TextField(blank=True)
