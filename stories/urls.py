from django.urls import path
from .views import (
    StoryListView,
    StoryDetailView,
    StoryCreateView,
    StoryUpdateView,
    StoryDeleteView,
    PublicStoriesDetailView,
    story_like_view,


)

app_name = 'stories'

urlpatterns = [
    path('', StoryListView.as_view(), name='story_list'),
    path('new/', StoryCreateView.as_view(), name='story_new'),
    path('<int:pk>/', StoryDetailView.as_view(), name='story_detail'),
    path('<int:pk>/edit/', StoryUpdateView.as_view(), name='story_edit'),
    path('<int:pk>/delete/', StoryDeleteView.as_view(), name='story_delete'),
    path('<int:pk>/', StoryDetailView.as_view(), name='story_detail'),
    path('share/<uuid:share_id>/', PublicStoriesDetailView.as_view(), name='story_share'),
    path('like/<int:pk>/', story_like_view, name='like_story'),
]