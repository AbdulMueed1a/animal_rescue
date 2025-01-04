from django.db import models

# Create your models here.
class submission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    location = models.CharField(max_length=100)
    description = models.TextField()
    condition = models.CharField(max_length=100)