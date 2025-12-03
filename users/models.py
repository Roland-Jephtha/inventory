from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and User.objects.count() == 0:
            self.role = self.Role.OWNER
        super().save(*args, **kwargs)
