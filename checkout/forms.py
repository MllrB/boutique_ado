from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number', 
                  'street_address1', 'street_address2', 'street_address3',
                  'town_or_city', 'county', 'post_code', 'country',)

    def __init__(self):
        """
        Add placeholders and classes, remove auto-generated
        labels and set focus on full name field
        """

        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name', 
            'email': 'Email Address',
            'phone_number': 'Phone Number', 
            'street_address1': 'Address Line 1',
            'street_address2': 'Address Line 2',
            'street_address3': 'Address Line 3',
            'town_or_city': 'Town/City',
            'county': 'County',
            'post_code': 'Postcode/Eircode',
            'country': 'Country'
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False
