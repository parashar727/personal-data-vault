from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return self.username
