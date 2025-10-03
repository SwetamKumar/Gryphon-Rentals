from django import forms
from .models import UserProfile

class PhonePasswordResetForm(forms.Form):
    """
    Form for requesting a password reset link via phone number.
    """
    COUNTRY_CODE_CHOICES = [
        ('+1', '+1'),
        ('+44', '+44'),
        ('+91', '+91'),
        ('+61', '+61'),
        ('+49', '+49'), # Add other country codes as needed
    ]
    country_code = forms.ChoiceField(
        choices=COUNTRY_CODE_CHOICES,
        widget=forms.Select(attrs={'id': 'countryCode', 'class': 'form-select'})
    )
    phone = forms.CharField(
        label="Phone Number",
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'id': 'phone'
        })
    )

    def clean(self):
        """
        Validates the phone number.

        Note: To prevent user enumeration attacks, we don't raise a
        ValidationError if the user doesn't exist. The view will handle
        this by showing a generic success message regardless.
        """
        cleaned_data = super().clean()
        # The view will perform the actual check for the user's existence.
        # You could add more complex validation here, e.g., using a library
        # like 'phonenumbers' to check for a valid phone number format.
        return cleaned_data