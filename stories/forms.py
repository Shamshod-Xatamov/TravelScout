from django import forms
from .models import Story,StoryComment
from django_summernote.widgets import SummernoteWidget
class StoryForm(forms.ModelForm):
    content = forms.CharField(widget=SummernoteWidget())
    class Meta:
        model = Story
        fields = ['title', 'location', 'cover_image', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'E.g., An Unforgettable Week in Paris'}),
            'location': forms.TextInput(attrs={'placeholder': 'E.g., Paris, France'}),
            'content': forms.Textarea(attrs={'rows': 15, 'placeholder': 'Tell your story here... Feel free to use Markdown!'}),
        }
        labels = {
            'title': 'Catchy Title',
            'location': 'Location of Your Story',
            'cover_image': 'Upload a beautiful cover image',
            'content': 'Your Story',
        }


class StoryCommentForm(forms.ModelForm):
    class Meta:
        model = StoryComment

        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Leave a comment...'}),
        }