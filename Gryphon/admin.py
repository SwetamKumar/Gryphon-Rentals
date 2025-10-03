from django.contrib import admin
from .models import UserProfile, Vehicle, Booking
admin.site.register(UserProfile)
admin.site.register(Vehicle)
admin.site.register(Booking)
