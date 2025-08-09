from django.db import models
from django.conf import settings
from django.urls import reverse

class TripPlan(models.Model):
    BUDGET_CHOICES=[
        ('Economy','Economy'),
        ('Standart','Standart'),
        ('Luxury','Luxury'),
    ]

    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


    destination=models.CharField(max_length=250)

    duration_days=models.PositiveIntegerField()

    interests=models.TextField()

    budget=models.CharField(max_length=10,choices=BUDGET_CHOICES)

    generated_plan=models.TextField(blank=True)

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sayohat rejasi: {self.destination})"
    def get_absolute_url(self):
        return reverse('trip_detail',args=[str(self.id)])