import random
import requests
import json
from django.shortcuts import render
from django.conf import settings
from .forms import ContinentForm
from .models import WeatherEntry

# API Endpoints
REST_COUNTRIES_API = "https://restcountries.com/v3.1/region/{continent}"
OPENWEATHER_API = "https://api.openweathermap.org/data/2.5/weather"

def continent_view(request):
    # Retrieve the API Key from settings.py
    api_key = settings.OPENWEATHERMAP_API_KEY

    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data['continent']
            results = []
            
            try:
                # Step 1: Fetch countries
                response = requests.get(REST_COUNTRIES_API.format(continent=continent), timeout=10)
                response.raise_for_status()
                all_countries = response.json()
                
                # Filter countries that actually have a capital city
                valid_countries = [c for c in all_countries if c.get('capital')]
                
                # Select 5 random countries
                selected_countries = random.sample(valid_countries, min(5, len(valid_countries)))

                # Step 2: Get weather
                for country in selected_countries:
                    name = country.get('name', {}).get('common', 'Unknown')
                    capital = country['capital'][0]
                    population = country.get('population', 'N/A')
                    
                    weather_params = {'q': capital, 'appid': api_key, 'units': 'metric'}
                    
                    try:
                        weather_res = requests.get(OPENWEATHER_API, params=weather_params, timeout=5)
                        weather_data = weather_res.json()
                        
                        if weather_res.status_code == 200:
                            temp = weather_data['main']['temp']
                            desc = weather_data['weather'][0]['description']
                        else:
                            temp = None
                            desc = f"Error: {weather_data.get('message', 'Not found')}"
                            
                    except Exception:
                        temp = None
                        desc = "Connection Error"

                    # Lat/Lon Logic
                    latlon = country.get('latlng', [])
                    coords = f"Lat: {latlon[0]}, Lon: {latlon[1]}" if len(latlon) == 2 else "N/A"

                    results.append({
                        'country': name,
                        'capital': capital,
                        'population': population,
                        'coords': coords,
                        'temp': temp,
                        'description': desc
                    })

                # Step 3: Save to MongoDB
                try:
                    WeatherEntry.objects.create(
                        continent=continent,
                        coordinates_str=coords,
                        results_json=results 
                    )
                    save_status = "Data saved to MongoDB successfully."
                except Exception as e:
                    save_status = f"MongoDB Error: {str(e)}"

                return render(request, 'geoapp/search_results.html', {
                    'results': results,
                    'save_status': save_status
                })

            except Exception as e:
                return render(request, 'geoapp/continent_form.html', {
                    'form': form,
                    'error': f"Error fetching data: {str(e)}"
                })
    else:
        form = ContinentForm()

    return render(request, 'geoapp/continent_form.html', {'form': form})

def history_view(request):
    try:
        history_list = WeatherEntry.objects.all().order_by('-timestamp')
        
        for entry in history_list:
            if isinstance(entry.results_json, list):
                entry.results_json = json.dumps(entry.results_json, indent=2)
                
    except Exception:
        history_list = []
        
    return render(request, 'geoapp/history.html', {'history': history_list})
