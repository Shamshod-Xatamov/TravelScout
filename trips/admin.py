
from django.contrib import admin
from .models import TripPlan

class TripPlanAdmin(admin.ModelAdmin):
    list_display = ('destination', 'user', 'duration_days', 'budget', 'created_at')
    list_filter = ('budget', 'user')

admin.site.register(TripPlan, TripPlanAdmin)