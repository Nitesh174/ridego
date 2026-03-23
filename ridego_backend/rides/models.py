from django.db import models
from users.models import User
from drivers.models import Driver


class Ride(models.Model):
    

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)

    pickup_location = models.CharField(max_length=200)
    drop_location = models.CharField(max_length=200)

    fare = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ('booked', 'Booked'),
            ('accepted', 'Accepted'),
            ('started', 'Started'),
            ('completed', 'Completed')
        ],
        default='booked'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ride {self.id}"
    commission = models.FloatField(default=0)
driver_earning = models.FloatField(default=0)