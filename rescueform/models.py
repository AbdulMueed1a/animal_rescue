from _datetime import date
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class submission(models.Model):
    STATUS_CHOICES = [
        ("received", "Report Received"),
        ("pending_verification", "Pending Verification"),
        ("verified", "Verified"),
        ("assigned", "Assigned to NGO/Hospital"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100)
    name = models.CharField(max_length=100)
    email = models.EmailField(null = False)
    animal = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    date = models.DateField(default=date.today)
    imgur_url = models.URLField(blank=True, null=True)
    # image = models.ImageField(upload_to='images/')
    latitude = models.FloatField(default=0.0,null=True, blank=True)
    longitude = models.FloatField(default=0.0,null=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200,null=True, blank=True)
    description = models.TextField()
    condition = models.CharField(max_length=100)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES,default="received")





class FCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s FCM Token"