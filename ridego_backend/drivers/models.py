from django.utils import timezone  

from django.db import models

class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20) 
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name