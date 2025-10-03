from django.db import models
from django.contrib.auth.models import User

# A simple Vehicle model. You can expand this later.
class Vehicle(models.Model):
    FUEL_CHOICES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('manual', 'Manual'), # For bikes
    )
    TRANSMISSION_CHOICES = (
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('none', 'None'), # For bikes
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # e.g., 'car', 'bike'
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    # New fields for richer details
    seats = models.PositiveIntegerField(default=5, help_text="Number of seats (for cars)")
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES, default='petrol')
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES, default='automatic')

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'myapp'

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending_payment', 'Pending Payment'),
        ('payment_failed', 'Payment Failed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    # Increased max_length to accommodate new status values
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pickup_location = models.CharField(max_length=100, default='Downtown')

    def __str__(self):
        return f"{self.vehicle.name} reservation for {self.user.username}"
