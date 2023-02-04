from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from libgravatar import Gravatar
from notes.helpers import validate_date
from colorfield.fields import ColorField


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
    name = models.CharField(max_length=10)

    class Meta:
        permissions = [
            ("dg_view_folder", "can view folder"),
            ("dg_edit_folder", "can edit folder"),
            ("dg_delete_folder", "can delete folder")
        ]

class Notebook(models.Model):
    user = models.ForeignKey(User, related_name="notebooks", on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name="notebooks", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=10)


class Page(models.Model):
    notebook = models.ForeignKey(Notebook, related_name="pages", on_delete=models.CASCADE)
    drawing = models.TextField(blank=True)
    
class Tag(models.Model):
    user = models.ForeignKey(User, related_name="tags", on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    COLOR_PALETTE = [
        ("#FFFFFF", "white", ),
        ("#000000", "black", ),
        ("#34eb67", "green", ),
    ]
    image = models.ImageField(upload_to="images",default=None)
    color = ColorField(image_field="image",samples=COLOR_PALETTE)


class Event(models.Model):
    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(default="")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    routine_choice =[
        ("0","No Repeat"),
        ("1","every Day" ),
        ("2","every Week"),
        ("3","every 2 Weeks"),
        ("4","every Month"),
        ("5","every Year"),
        ("Custom","Custom")
    ]
    week_choice =[
        ("Monday","Monday" ),
        ("Tuesday","Tuesday"),
        ("Wednesday","Wednesday"),
        ("Thursday","Thursday"),
        ("Friday","Friday"),
        ("Saturday","Saturday"),
        ("Sunday","Sunday"),
    ]
    routine = models.CharField(choices=routine_choice , max_length=10)
    tag = models.OneToOneField(Tag , related_name='tag',on_delete=models.CASCADE,null=True)

