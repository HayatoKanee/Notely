from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from libgravatar import Gravatar


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

# Create your models here.
