from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)

class Vehicle(models.Model):
    VEHICLE_TYPE = (
        ('car', 'Car'),
        ('bike', 'Bike'),
    )
    vehicle_type = models.CharField(choices=VEHICLE_TYPE, max_length=10)
    model = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='available')
    location = models.CharField(max_length=100)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='active')

class Vehicles(models.Model):
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
def __str__(self):
        return self.name
