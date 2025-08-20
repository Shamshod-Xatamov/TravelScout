from django.urls import path
from .views import flight_search_view
app_name = 'flights'

urlpatterns = [
    path('search/', flight_search_view, name='flight_search'),
]