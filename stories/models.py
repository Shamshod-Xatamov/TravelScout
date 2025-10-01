
from django.db import models
from django.conf import settings
from django.db.models import TextField
from django.urls import reverse
import uuid

class Story(models.Model):
    title=models.CharField(max_length=200)
    content=TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    author=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    location=models.CharField(max_length=100,blank=True)
    cover_image=models.ImageField(upload_to='story_covers/',blank=True,null=True)
    view_count = models.PositiveIntegerField(default=0)
    share_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_stories', blank=True)
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('stories:story_detail',kwargs={'pk':self.pk})


class StoryComment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)