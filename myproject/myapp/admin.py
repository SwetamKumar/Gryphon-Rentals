from django.contrib import admin, messages
from .models import Vehicle, Reservation, UserProfile

# A simple admin registration for the Vehicle model for better management
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price_per_day', 'fuel_type', 'transmission')
    list_filter = ('type', 'fuel_type', 'transmission')
    search_fields = ('name',)

# Custom admin configuration for the Reservation model
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    
    # --- The Custom Admin Action ---
    def mark_as_payment_approved(self, request, queryset):
        """
        Admin action to change the status of selected reservations to 'active'.
        This is for manually approving payments.
        """
        # We only want to approve payments for reservations that are pending or have failed.
        updatable_queryset = queryset.filter(status__in=['pending_payment', 'payment_failed'])
        
        updated_count = updatable_queryset.update(status='active')
        
        self.message_user(request, f"{updated_count} reservations were successfully marked as active.", messages.SUCCESS)

    # Set a user-friendly description for the action in the admin dropdown
    mark_as_payment_approved.short_description = "Approve payment for selected reservations"

    # --- Admin List View Configuration ---
    list_display = ('id', 'user', 'vehicle', 'start_date', 'end_date', 'status', 'total_cost')
    list_filter = ('status', 'vehicle__type', 'start_date')
    search_fields = ('user__username', 'user__email', 'vehicle__name')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    
    # Add the custom action to the list of available actions
    actions = [mark_as_payment_approved]

# Optional: Register UserProfile if you want to see it in the admin
admin.site.register(UserProfile)