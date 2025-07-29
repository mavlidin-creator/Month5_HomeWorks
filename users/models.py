from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)

    def generate_confirmation_code(self):
        self.confirmation_code = str(random.randint(100000, 999999))
        self.save()
