from webbrowser import register

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView,UpdateView
from .forms import CustomUserCreationForm,CustomUserChangeForm
from .models import CustomUser
from django.contrib.messages.views import SuccessMessageMixin

class SignUpView(CreateView):
    form_class=CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProfileUpdateView(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('my_plans_list')
    success_message = "Your profile was updated successfully!"

    def get_object(self):
        return self.request.user
