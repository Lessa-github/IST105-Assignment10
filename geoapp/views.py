# geoapp/views.py
import random
import requests
import json
from django.shortcuts import render
from django.conf import settings # To access the secure API Key
from .forms import ContinentForm
from .models import WeatherEntry

# API Endpoints
REST_COUNTRIES_API = "https://restcountries.com/v3.1/region/{continent}"
OPENWEATHER_API = "https://api.openweathermap.org/data/2.5/weather"

def continent_view(request):
    # Retrieve the API Key from settings.py (which reads from .env)
    api_key = settings.OPENWEATHERMAP_API_KEY

    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data['continent']
            results = []
            
            try:
                # Step 1: Fetch countries from the selected continent
                response = requests.get(REST_COUNTRIES_API.format(continent=continent), timeout=10)
                response.raise_for_status()
                all_countries = response.json()
                
                # Filter countries that actually have a capital city
                valid_countries = [c for c in all_countries if c.get('capital')]
                
                # Select 5 random countries (or fewer if not enough exist)
                selected_countries = random.sample(valid_countries, min(5, len(valid_countries)))

                # Step 2: Loop through countries to get weather
                for country in selected_countries:
                    name = country.get('name', {}).get('common', 'Unknown')
                    capital = country['capital'][0] # Capital is a list, get first item
                    population = country.get('population', 'N/A')
                    
                    # Fetch weather for the capital
                    weather_params = {
                        'q': capital,
                        'appid': api_key,
                        'units': 'metric'
                    }
                    
                    try:
                        weather_res = requests.get(OPENWEATHER_API, params=weather_params, timeout=5)
                        weather_data = weather_res.json()
                        
                        if weather_res.status_code == 200:
                            temp = weather_data['main']['temp']
                            desc = weather_data['weather'][0]['description']
                        else:
                            temp = None
                            desc = f"Error: {weather_data.get('message', 'Not found')}"
                            
                    except Exception as e:
                        temp = None
                        desc = "Connection Error"

                    # Add to results list
                    results.append({
                        'country': name,
                        'capital': capital,
                        'population': population,
                        'temp': temp,
                        'description': desc
                    })

                # Step 3: Save results to MongoDB using the Model
                try:
                    WeatherEntry.objects.create(
                        continent=continent,
                        results_json=json.dumps(results) # Convert list to string for storage
                    )
                    save_status = "Data saved to MongoDB successfully."
                except Exception as e:
                    save_status = f"MongoDB Error: {str(e)}"

                # Render the results page
                return render(request, 'geoapp/search_results.html', {
                    'results': results,
                    'save_status': save_status
                })

            except Exception as e:
                # Handle general API errors (e.g., REST Countries down)
                return render(request, 'geoapp/continent_form.html', {
                    'form': form,
                    'error': f"Error fetching data: {str(e)}"
                })
    else:
        form = ContinentForm()

    return render(request, 'geoapp/continent_form.html', {'form': form})

def history_view(request):
    # Fetch all entries from MongoDB, sorted by newest first
    try:
        history = WeatherEntry.objects.all().order_by('-timestamp')
    except Exception as e:
        history = []
        
    return render(request, 'geoapp/history.html', {'history': history})
