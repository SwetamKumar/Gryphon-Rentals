from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    # The landing page with login/register modals
    path('', views.index_view, name='index'), # This line is correct for the landing page
    # The main page after logging in
    path('home/', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('vehicles/', views.vehicle_list, name='vehicles'),
    path('about/', views.about, name='about'), # This line is correct for the about page
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms_view, name='terms'),
    path('policy/', views.policy_view, name='policy'),
    path('profile/add-phone/', views.add_phone_number_view, name='add_phone_number'),


    # API endpoints for frontend JavaScript
    path('api/vehicles/', views.vehicle_data_view, name='vehicle_data'),
    path('api/vehicle/<int:vehicle_id>/booked-dates/', views.get_booked_dates_view, name='get_booked_dates'),
    path('api/rent/', views.rent_vehicle_view, name='rent_vehicle'),
    path('payment/<int:reservation_id>/', views.payment_page, name='payment_page'),
    path('process-payment/', views.process_payment, name='process_payment'),
]
