from django.contrib import admin
from .models import Story

class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'view_count']
    list_filter = ['author', 'created_at']
    search_fields = ['title', 'content']


admin.site.register(Story, StoryAdmin)