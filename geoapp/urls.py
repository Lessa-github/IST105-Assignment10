# geoapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Route for the main search page
    path('', views.continent_view, name='continent_search'),
    
    # Route for the history page
    path('history/', views.history_view, name='search_history'),
]
