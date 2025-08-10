from django.urls import path


from .views import TripPlanCreateView, TripPlanDetailView,TripPlanListView,TripPlanUpdateView,TripPlanDeleteView,trip_plan_pdf_view,HomePageView

urlpatterns=[
    path('', HomePageView.as_view(), name='home'),
    path('trip/new/',TripPlanCreateView.as_view(),name='trip_new'),
    path('trip/<int:pk>/',TripPlanDetailView.as_view(),name='trip_detail'),
    path('my-plans/', TripPlanListView.as_view(), name='my_plans_list'),
    path('trip/<int:pk>/edit/', TripPlanUpdateView.as_view(), name='trip_edit'),
    path('trip/<int:pk>/delete/', TripPlanDeleteView.as_view(), name='trip_delete'),
    path('trip/<int:pk>/pdf/', trip_plan_pdf_view, name='trip_pdf'),
]