from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Subscription Fields
    class SubscriptionStatus(models.TextChoices):
        TRIAL = "TRIAL", "Trial"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        GRACE = "GRACE", "Grace Period"

    subscription_status = models.CharField(
        max_length=20, 
        choices=SubscriptionStatus.choices, 
        default=SubscriptionStatus.TRIAL
    )
    trial_start_date = models.DateTimeField(default=timezone.now)
    subscription_end_date = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.pk and User.objects.count() == 0:
            self.role = self.Role.OWNER
        super().save(*args, **kwargs)
