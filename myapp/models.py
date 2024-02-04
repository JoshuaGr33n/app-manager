from django.db import models
from django.conf import settings
import uuid
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, date

# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=20)
    

class App(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apps')
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    class Meta:
        # A unique constraint on the 'name' and 'user' fields
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_name_for_user')
        ]

    def __str__(self):
        return self.name


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    FREE = 'free'
    STANDARD = 'standard'
    PRO = 'pro'

    PLAN_CHOICES = [
        (FREE, 'Free'),
        (STANDARD, 'Standard'),
        (PRO, 'Pro'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, default=FREE)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
    
    
    
class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # app = models.ForeignKey(App, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.start_date: 
            self.start_date = date.today()  
        if not self.end_date:  # Only calculate end_date if it's not already set
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.app.name} - {self.plan.name}"

    