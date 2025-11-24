# geoapp/forms.py
from django import forms

class ContinentForm(forms.Form):
    # Options for the dropdown menu
    CONTINENT_CHOICES = [
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('Africa', 'Africa'),
        ('Americas', 'Americas'),
        ('Oceania', 'Oceania'),
    ]
    
    # The dropdown field rendered in HTML
    continent = forms.ChoiceField(
        label='Select a Continent',
        choices=CONTINENT_CHOICES
    )
