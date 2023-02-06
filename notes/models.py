from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from libgravatar import Gravatar

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
            path.insert(0,current)
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
