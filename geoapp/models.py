# geoapp/models.py
from djongo import models
from django.utils import timezone

class WeatherEntry(models.Model):
    # Stores the continent selected by the user
    continent = models.CharField(max_length=50)
          
    results_json = models.JSONField()
    
    # Auto-generates the timestamp when the record is created
    timestamp = models.DateTimeField(default=timezone.now)

    coordinates_str = models.CharField(max_length=50, default='N/A')

    def __str__(self):
        return f"Search for {self.continent} at {self.timestamp}"

    class Meta:
        # Define the collection name in MongoDB
        db_table = 'weather_entries'
