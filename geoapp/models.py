# geoapp/models.py
from django.db import models
from django.utils import timezone

class WeatherEntry(models.Model):
    # Stores the continent selected by the user
    continent = models.CharField(max_length=50)
    
    # Stores the full results list as a text string (JSON format)
    # This avoids complex relationships for this simple assignment
    results_json = models.TextField()
    
    # Auto-generates the timestamp when the record is created
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Search for {self.continent} at {self.timestamp}"

    class Meta:
        # Define the collection name in MongoDB
        db_table = 'weather_entries'
