from django.urls import path
from .views import support_view

app_name = 'support'

urlpatterns = [
    path('', support_view, name='contact'),
]