from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.contrib.auth.models import User
from .models import Reservation, Vehicle, UserProfile
import json
from django.urls import reverse
from django.conf import settings
from datetime import date, datetime
from django.db.models import Sum, Count, Value, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index_view(request):
    """
    Renders the main landing/login page.
    If the user is already authenticated, it redirects them to the home/dashboard page.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'index.html')

def register_view(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('registerPassword')
        phone_number = request.POST.get('phone')
        country_code = request.POST.get('registerCountryCode')

        # Basic validation
        if not all([first_name, last_name, email, password]):
            messages.error(request, 'All fields are required for registration.')
            return redirect('index')
        
        # Check if user already exists using a case-insensitive lookup.
        if User.objects.filter(username__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return redirect('index')

        # Create new user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # If a phone number was provided, create a UserProfile for it
        if phone_number:
            full_phone = f"{country_code}{phone_number.strip()}"
            # Prevent duplicate phone numbers
            if UserProfile.objects.filter(phone=full_phone).exists():
                user.delete() # Clean up the created user
                messages.error(request, 'This phone number is already associated with another account.')
                return redirect('index')
            UserProfile.objects.create(user=user, phone=full_phone)

        # Log the user in and redirect to the home page
        login(request, user)
        messages.success(request, f'Welcome, {first_name}! Your registration was successful.')
        return redirect('home')
    
    return redirect('index')

def login_view(request):
    if request.method == 'POST':
        # Check if this is a phone login by looking for the 'loginPhone' field
        if 'loginPhone' in request.POST and request.POST.get('loginPhone'):
            country_code = request.POST.get('countryCode', '+1')
            phone_number = request.POST.get('loginPhone').strip()
            password = request.POST.get('loginPassword')
            full_phone = f"{country_code}{phone_number}"

            user = None
            try:
                # Find the user profile associated with the phone number
                user_profile = UserProfile.objects.select_related('user').get(phone=full_phone)
                # Authenticate using the associated user object
                user = authenticate(request, username=user_profile.user.username, password=password)
            except UserProfile.DoesNotExist:
                pass # user will remain None

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid phone number or password.')
                return redirect('index')

        # --- Fallback to Email Login ---
        else:
            email = request.POST.get('loginEmail')
            password = request.POST.get('loginPassword')

            # First, find the user with a case-insensitive lookup on the email/username.
            try:
                user_obj = User.objects.get(username__iexact=email)
            except User.DoesNotExist:
                user_obj = None

            if user_obj:
                # If the user is found, authenticate using their actual username to respect case-sensitivity in the password check.
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')

            # If the user is not found or the password is wrong, show a generic error.
            messages.error(request, 'Invalid email or password.')
            return redirect('index')
            
    return redirect('index')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('index')

@login_required
def home_view(request):
    """
    Renders the main dashboard, including vehicle listings and user reservations.
    Handles POST requests to update reservation status.
    """
    # Handle POST request first to update a reservation's status
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        action = request.POST.get('action')
        try:
            # Ensure the reservation belongs to the current user before updating
            reservation = Reservation.objects.get(id=reservation_id, user=request.user)
            if reservation.status == 'active':
                if action == 'complete':
                    reservation.status = 'completed'
                    reservation.save()
                    messages.success(request, f'Reservation for "{reservation.vehicle.name}" marked as completed.')
                elif action == 'cancel':
                    reservation.status = 'cancelled'
                    reservation.save()
                    messages.success(request, f'Reservation for "{reservation.vehicle.name}" has been cancelled.')
            else:
                messages.warning(request, 'This reservation is not active and cannot be changed.')
        except Reservation.DoesNotExist:
            messages.error(request, 'Reservation not found or you do not have permission to modify it.')
        # Redirect back to the home page to show the result
        return redirect('home') 

    # --- Handle GET request ---

    # 1. Automatically update status of any rentals whose end date has passed.
    # This is more efficient than looping in Python.
    Reservation.objects.filter(user=request.user, status='active', end_date__lt=date.today()).update(status='completed')

    # 2. Fetch all reservations for the logged-in user
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-start_date')

    # 3. --- Rental Statistics Calculation ---
    total_rentals = user_reservations.count()
    active_rentals = user_reservations.filter(status='active').count()
    pending_rentals = user_reservations.filter(status__in=['pending_payment', 'payment_failed']).count()

    # Calculate total spent on completed rentals, defaulting to 0 if none.
    total_spent = user_reservations.filter(status='completed').aggregate(
        total=Coalesce(Sum('total_cost'), Value(0, output_field=DecimalField()))
    )['total']

    # Determine favorite vehicle type
    type_counts = user_reservations.values('vehicle__type').annotate(
        count=Count('vehicle__type')
    ).order_by('-count')

    # Safely get the favorite type
    first_type = type_counts.first()
    if first_type and first_type['vehicle__type']:
        favorite_type = first_type['vehicle__type'].capitalize()
    else:
        favorite_type = 'N/A'

    # Fetch user profile to display phone number
    user_profile = None
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        pass # It's okay if the user doesn't have a profile yet

    context = {
        'reservations': user_reservations,
        'total_rentals': total_rentals,
        'active_rentals': active_rentals,
        'pending_rentals': pending_rentals,
        'total_spent': total_spent,
        'favorite_type': favorite_type,
        'user_profile': user_profile,
    }
    return render(request, 'home.html', context)

def vehicle_list(request):
    """
    Renders a standalone page listing vehicles, with support for filtering.
    """
    # Get the filter from the query parameter, default to 'all'
    vehicle_filter = request.GET.get('filter', 'all')

    # Start with all vehicles, ordered by name
    vehicles = Vehicle.objects.all().order_by('name')

    # Apply the filter based on the query parameter
    if vehicle_filter == 'car':
        vehicles = vehicles.filter(type='car')
    elif vehicle_filter == 'bike':
        vehicles = vehicles.filter(type='bike')
    elif vehicle_filter == 'electric':
        vehicles = vehicles.filter(fuel_type='electric')

    context = {
        'vehicles': vehicles,
        'active_filter': vehicle_filter,  # To highlight the active filter button
    }
    return render(request, 'vehicles.html', context)

def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')

def terms_view(request):
    return render(request, 'terms.html')

def policy_view(request):
    return render(request, 'policy.html')

def vehicle_data_view(request):
    """
    Provides vehicle data as JSON to be used by the frontend JavaScript.
    Now supports filtering, searching, and pagination.
    """
    # Get filter, search, and page from query parameters
    vehicle_type_filter = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    # Start with all vehicles, ordered for consistent pagination
    vehicle_list = Vehicle.objects.all().order_by('name')

    # Apply filters from the request
    if vehicle_type_filter == 'car':
        vehicle_list = vehicle_list.filter(type='car')
    elif vehicle_type_filter == 'bike':
        vehicle_list = vehicle_list.filter(type='bike')
    elif vehicle_type_filter == 'electric':
        vehicle_list = vehicle_list.filter(fuel_type='electric')

    # Apply search query if it exists
    if search_query:
        vehicle_list = vehicle_list.filter(name__icontains=search_query)

    # Set up pagination with 6 vehicles per page
    paginator = Paginator(vehicle_list, 6)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    # Serialize the vehicle data for the current page
    vehicles_on_page = []
    for v in page_obj.object_list:
        # Build a dynamic list of features based on vehicle type
        features = []
        if v.type == 'car':
            features.append(f"{v.get_transmission_display()}")
            features.append(f"{v.seats} Seats")
        features.append(f"Fuel: {v.get_fuel_type_display()}")

        vehicle_data = {
            'id': v.id,
            'name': v.name,
            'type': v.type,
            'price': float(v.price_per_day),
            'priceUnit': 'day',
            'image': v.image_url or '/static/images/default.png', # Provide a default
            'features': features
        }
        # Add 'tags' if the vehicle is electric so the filter works
        if v.fuel_type == 'electric':
            vehicle_data['tags'] = ['electric']
        vehicles_on_page.append(vehicle_data)

    # Return a structured response with pagination info
    return JsonResponse({
        'vehicles': vehicles_on_page,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })

@login_required
def get_booked_dates_view(request, vehicle_id):
    """
    Returns a list of booked date ranges for a specific vehicle
    in a format that flatpickr can understand.
    """
    try:
        # We only care about reservations that are currently 'active'
        reservations = Reservation.objects.filter(
            vehicle_id=vehicle_id,
            status='active'
        )
        
        booked_dates = [
            {"from": res.start_date.strftime('%Y-%m-%d'), "to": res.end_date.strftime('%Y-%m-%d')}
            for res in reservations
        ]
        return JsonResponse(booked_dates, safe=False)
    except Vehicle.DoesNotExist:
        return JsonResponse({'error': 'Vehicle not found'}, status=404)

@login_required
def rent_vehicle_view(request):
    """
    Handles the creation of a new reservation via a POST request from the frontend.
    The reservation is created with a 'pending_payment' status.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data.get('vehicle_id')
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            pickup_location = data.get('pickup_location')

            if not all([vehicle_id, start_date_str, end_date_str, pickup_location]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)

            vehicle = Vehicle.objects.get(id=vehicle_id)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if start_date < date.today() or end_date <= start_date:
                return JsonResponse({'status': 'error', 'message': 'Invalid date range.'}, status=400)

            # --- Check for booking conflicts ---
            # A vehicle is unavailable if another active reservation overlaps with the requested dates.
            # Overlap exists if: existing_start_date < new_end_date AND existing_end_date > new_start_date
            conflicting_reservations = Reservation.objects.filter(
                vehicle=vehicle,
                status='active',
                start_date__lt=end_date,
                end_date__gt=start_date
            ).exists()

            if conflicting_reservations:
                return JsonResponse({'status': 'error', 'message': 'This vehicle is already booked for some of the selected dates. Please choose different dates.'}, status=409) # 409 Conflict

            # Server-side cost calculation for security
            duration = (end_date - start_date).days
            total_cost = vehicle.price_per_day * duration

            # Create the reservation with a 'pending_payment' status
            new_reservation = Reservation.objects.create(
                user=request.user,
                vehicle=vehicle,
                start_date=start_date,
                end_date=end_date,
                pickup_location=pickup_location.capitalize(),
                total_cost=total_cost,
                status='pending_payment'  # Explicitly set status
            )
            
            # Instead of a generic success message, return a URL to the payment page
            payment_url = reverse('payment_page', args=[new_reservation.id])
            return JsonResponse({
                'status': 'success', 
                'message': 'Reservation initiated. Please proceed to payment.',
                'redirect_url': payment_url
            })

        except Vehicle.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Vehicle not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def payment_page(request, reservation_id):
    """
    Displays the payment page for a specific reservation.
    """
    # Ensure the reservation exists and belongs to the logged-in user
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    # User can only pay for reservations that are pending or have failed.
    if reservation.status not in ['pending_payment', 'payment_failed']:
        messages.warning(request, "This reservation cannot be paid for at this time.")
        return redirect('home')

    return render(request, 'payment.html', {'reservation': reservation})

@login_required
def process_payment(request):
    """
    Processes the dummy payment form submission.
    """
    if request.method != 'POST':
        return redirect('home')

    reservation_id = request.POST.get('reservation_id')
    cvv = request.POST.get('cvv')
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    # --- Dummy Payment Condition ---
    # For this demo, a CVV of "123" will succeed, anything else will fail.
    if cvv == "123":
        # PAYMENT SUCCESS
        reservation.status = 'active'
        reservation.save()
        
        return render(request, 'payment_status.html', {
            'title': 'Payment Successful',
            'message': f'Your payment was successful! Your rental for "{reservation.vehicle.name}" is confirmed.',
            'redirect_url': reverse('home')
        })
    else:
        # PAYMENT FAILURE
        reservation.status = 'payment_failed'
        reservation.save()
        messages.error(request, "Your payment failed. You can retry from the 'My Reservations' section.")
        return redirect('home')
@login_required
def add_phone_number_view(request):
    """
    Allows a logged-in user to add a phone number to their profile.
    """
    if request.method == 'POST':
        phone_number = request.POST.get('phone', '').strip()
        country_code = request.POST.get('countryCode', '+1')

        if not phone_number:
            messages.error(request, 'Phone number cannot be empty.')
            return redirect('home')

        full_phone = f"{country_code}{phone_number}"

        # Check if this phone number is already in use by another user
        if UserProfile.objects.filter(phone=full_phone).exclude(user=request.user).exists():
            messages.error(request, 'This phone number is already associated with another account.')
            return redirect('home')

        # Use update_or_create to handle cases where a UserProfile might exist without a phone
        UserProfile.objects.update_or_create(
            user=request.user,
            defaults={'phone': full_phone}
        )
        
        messages.success(request, 'Your phone number has been added successfully.')
    return redirect('home')
