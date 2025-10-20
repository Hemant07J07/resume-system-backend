# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model — extend here if needed."""
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
