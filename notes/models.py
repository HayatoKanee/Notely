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

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=30)


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
