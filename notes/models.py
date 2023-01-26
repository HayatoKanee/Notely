from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """User model used for authentication"""
    user_id = models.IntegerField(unique=True,blank=False, primary_key=True)
    username = models.CharField(unique=True, blank=False, max_length=50)
    email = models.EmailField(unique=True, blank=False)
    password = models.CharField(blank=False, max_length=10)

# Create your models here.
