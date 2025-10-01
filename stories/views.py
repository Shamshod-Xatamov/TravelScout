from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect,render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Story,StoryComment
from .forms import StoryForm,StoryCommentForm
from django.contrib import messages
class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    form_class = StoryForm
    template_name = 'stories/story_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class StoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Story
    form_class = StoryForm
    template_name = 'stories/story_form.html'

    def test_func(self):
        story = self.get_object()
        return self.request.user == story.author

    def form_valid(self, form):
        messages.success(self.request, f"Your story '{self.object.title}' has been updated successfully!")
        return super().form_valid(form)


class StoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Story
    template_name = 'stories/story_confirm_delete.html'
    success_url = reverse_lazy('stories:story_list')

    def test_func(self):
        story = self.get_object()
        return self.request.user == story.author

class StoryListView(ListView):
    model=Story
    template_name = 'stories/story_list.html'
    context_object_name = 'stories'
    ordering = ['-created_at']


class StoryDetailView(DetailView):
    model = Story
    template_name = 'stories/story_detail.html'
    context_object_name = 'story'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story_object = self.get_object()
        context['comments'] = story_object.comments.all().order_by('-created_at')
        context['comment_form'] = StoryCommentForm()
        return context


    def post(self, request, *args, **kwargs):
        story = self.get_object()

        form = StoryCommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.story = story
            new_comment.user = self.request.user
            new_comment.save()
            messages.success(self.request, "Your comment has been posted!")
            return redirect(story.get_absolute_url())
        else:
            self.object = story
            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)


class PublicStoriesDetailView(DetailView):
    model = Story
    template_name = 'stories/story_detail.html'
    context_object_name = 'story'
    slug_field = 'share_id'
    slug_url_kwarg = 'share_id'


@login_required
def story_like_view(request, pk):
    story = get_object_or_404(Story, id=pk)

    if request.method == 'POST':
        user = request.user
        if user in story.likes.all():
            story.likes.remove(user)
            context = {'story': story}
            return render(request, 'stories/partials/like_button.html', context)
        else:
            story.likes.add(user)
            context = {'story': story}
            return render(request, 'stories/partials/unlike_button.html', context)

    return redirect(story.get_absolute_url())


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(StoryComment, pk=pk)
    story_pk = comment.story.pk

    if request.method == 'POST':
        comment.delete()
        return redirect('stories:story_detail', pk=story_pk)
    return redirect('stories:story_detail', pk=story_pk)