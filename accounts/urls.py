
from django.urls import path
from .views import SignUpView,ProfileUpdateView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
]