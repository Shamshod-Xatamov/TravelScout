import os


from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.urls import reverse_lazy
from .models import TripPlan
import google.generativeai as genai

try:
    api_key=os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model=genai.GenerativeModel('gemini-1.5-flash-latest')
    else:
        model=None
        print("GOOGLE_API_KEY topilmadi. .env faylini tekshiring.")
except Exception as e:
    print(f"Google AI'ni sozlashda xatolik: {e}")
    model = None

class TripPlanCreateView(LoginRequiredMixin,CreateView):
    model=TripPlan
    template_name = 'home.html'
    fields = ['destination','duration_days','interests','budget']

    def form_valid(self, form):
        form.instance.user=self.request.user

        destination=form.cleaned_data.get('destination')
        duration = form.cleaned_data.get('duration_days')
        interests = form.cleaned_data.get('interests')
        budget = form.cleaned_data.get('budget')

        ai_generated_plan = "Xatolik: Reja tuzib bo'lmadi. API kalitini tekshiring."
        if model:
            try:
                # AI uchun prompt (so'rov matni)
                prompt = f"""
                Act as a world-class, expert travel consultant named 'Scout'. Your tone is enthusiastic, helpful, and highly detailed.

                **Task:** Create a personalized travel itinerary based on the following user preferences.

                **User Preferences:**
                *   **Destination:** {destination}
                *   **Trip Duration:** {duration} days
                *   **Primary Interests:** {interests}
                *   **Budget Level:** {budget}

                **Output Requirements:**
                1.  **Title:** Start with a creative and exciting title for the trip.
                2.  **Introduction:** Write a short, welcoming paragraph that gets the user excited about their trip.
                3.  **Day-by-Day Itinerary:**
                    *   For each day (Day 1, Day 2, etc.), provide a structured plan for "Morning", "Afternoon", and "Evening".
                    *   For each activity, provide a brief, compelling description.
                    *   Suggest specific places, landmarks, or activities.
                4.  **Practical Tips (for each day):**
                    *   **Food Recommendation:** Suggest one or two specific, highly-rated local restaurants, cafes, or street food spots that fit the user's budget. Briefly mention what kind of food they are famous for.
                    *   **Transportation Tip:** Provide a useful tip on how to get around for that day's activities (e.g., "Use the Metro Line A for this part of the city," or "This area is best explored on foot.").
                5.  **Formatting:**
                    *   **Use Markdown extensively.** Use headings (`## Day 1`), bold text (`**Colosseum**`), and bullet points (`-`) to make the plan easy to read and scan.
                    *   Do not include any pre-text or post-text like "Here is your plan:". Start directly with the title.
                """

                response = model.generate_content(prompt)

                ai_generated_plan = response.text

            except Exception as e:
                print(f"Google AI'ga so'rov yuborishda xatolik: {e}")
                ai_generated_plan = f"Reja tuzishda xatolik yuz berdi: {e}"
        form.instance.generated_plan=ai_generated_plan
        return super().form_valid(form)

class TripPlanDetailView(LoginRequiredMixin,DetailView):
    model=TripPlan
    template_name = 'trip_detail.html'
    context_object_name = 'trip'

class TripPlanListView(LoginRequiredMixin,ListView):
    model=TripPlan
    template_name = 'my_plans.html'
    context_object_name = 'plans_list'

    def get_queryset(self):
        return TripPlan.objects.filter(user=self.request.user).order_by('-created_at')



class TripPlanUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=TripPlan
    fields = ('destination', 'duration_days', 'interests', 'budget')
    template_name = 'trip_edit.html'

    def form_valid(self, form):
        form.instance.user=self.request.user

        destination=form.cleaned_data.get('destination')
        duration = form.cleaned_data.get('duration_days')
        interests = form.cleaned_data.get('interests')
        budget = form.cleaned_data.get('budget')

        ai_generated_plan = "Xatolik: Reja tuzib bo'lmadi. API kalitini tekshiring."
        if model:
            try:
                # AI uchun prompt (so'rov matni)
                prompt = f"""
                Act as a world-class, expert travel consultant named 'Scout'. Your tone is enthusiastic, helpful, and highly detailed.

                **Task:** Create a personalized travel itinerary based on the following user preferences.

                **User Preferences:**
                *   **Destination:** {destination}
                *   **Trip Duration:** {duration} days
                *   **Primary Interests:** {interests}
                *   **Budget Level:** {budget}

                **Output Requirements:**
                1.  **Title:** Start with a creative and exciting title for the trip.
                2.  **Introduction:** Write a short, welcoming paragraph that gets the user excited about their trip.
                3.  **Day-by-Day Itinerary:**
                    *   For each day (Day 1, Day 2, etc.), provide a structured plan for "Morning", "Afternoon", and "Evening".
                    *   For each activity, provide a brief, compelling description.
                    *   Suggest specific places, landmarks, or activities.
                4.  **Practical Tips (for each day):**
                    *   **Food Recommendation:** Suggest one or two specific, highly-rated local restaurants, cafes, or street food spots that fit the user's budget. Briefly mention what kind of food they are famous for.
                    *   **Transportation Tip:** Provide a useful tip on how to get around for that day's activities (e.g., "Use the Metro Line A for this part of the city," or "This area is best explored on foot.").
                5.  **Formatting:**
                    *   **Use Markdown extensively.** Use headings (`## Day 1`), bold text (`**Colosseum**`), and bullet points (`-`) to make the plan easy to read and scan.
                    *   Do not include any pre-text or post-text like "Here is your plan:". Start directly with the title.
                """

                response = model.generate_content(prompt)

                ai_generated_plan = response.text

            except Exception as e:
                print(f"Google AI'ga so'rov yuborishda xatolik: {e}")
                ai_generated_plan = f"Reja tuzishda xatolik yuz berdi: {e}"
        form.instance.generated_plan=ai_generated_plan
        return super().form_valid(form)


    def test_func(self):
        plan=self.get_object()
        return self.request.user==plan.user

class TripPlanDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=TripPlan
    template_name = "trip_confirm_delete.html"
    success_url = reverse_lazy('my_plans_list')

    def test_func(self):
        plan = self.get_object()
        return self.request.user == plan.user