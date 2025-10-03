from django.shortcuts import render, redirect
from .models import Vehicle, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from random import randint

otp_store = {}

def index(request):
    cars = Vehicle.objects.filter(vehicle_type='car')
    bikes = Vehicle.objects.filter(vehicle_type='bike')
    return render(request, 'index.html', {'cars': cars, 'bikes': bikes})

def send_otp(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        otp = str(randint(1000, 9999))
        otp_store[phone] = otp
        # Simulate sending SMS (replace with Twilio or similar)
        print(f"OTP for {phone}: {otp}")
        messages.info(request, f"OTP sent to {phone}")
        return render(request, 'verify_otp.html', {'phone': phone})
    return redirect('index')

def verify_otp(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        otp_input = request.POST['otp']
        if otp_store.get(phone) == otp_input:
            user, created = User.objects.get_or_create(username=phone)
            UserProfile.objects.get_or_create(user=user, phone=phone)
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect('index')
        else:
            messages.error(request, "Invalid OTP")
    return redirect('index')