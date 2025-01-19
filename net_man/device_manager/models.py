from django.db import models

# Create your models here.
from django.db import models

class Device(models.Model):
    ip_address = models.GenericIPAddressField()
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)  # Indicates if the device is online
    last_checked = models.DateTimeField(auto_now=True)

class Configuration(models.Model):
    scanning_enabled = models.BooleanField(default=True)
