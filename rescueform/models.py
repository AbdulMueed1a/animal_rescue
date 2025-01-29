from _datetime import date
from webpush import send_group_notification
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
    email = models.EmailField()
    animal = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    date = models.DateField(default=date.today)
    image = models.ImageField(upload_to='images/')
    latitude = models.FloatField(default=0.0,null=True, blank=True)
    longitude = models.FloatField(default=0.0,null=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200,null=True, blank=True)
    description = models.TextField()
    condition = models.CharField(max_length=100)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES,default="received")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        payload = {
            "head": f"New Post! {self.animal} {self.condition}",
            "body": self.description ,
            "url": f"/posts/{self.id}/"  # URL to redirect when the notification is clicked
        }
        send_group_notification(group_name="Subscribers", payload=payload)
    # condition = models.