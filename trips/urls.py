from django.urls import path


from .views import TripPlanCreateView, TripPlanDetailView,TripPlanListView,TripPlanUpdateView,TripPlanDeleteView

urlpatterns=[
    path('',TripPlanCreateView.as_view(),name='home'),
    path('trip/<int:pk>/',TripPlanDetailView.as_view(),name='trip_detail'),
    path('my-plans/', TripPlanListView.as_view(), name='my_plans_list'),
    path('trip/<int:pk>/edit/', TripPlanUpdateView.as_view(), name='trip_edit'),
    path('trip/<int:pk>/delete/', TripPlanDeleteView.as_view(), name='trip_delete'),
]