import os


from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.urls import reverse_lazy
from .models import TripPlan
import google.generativeai as genai
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.messages.views import SuccessMessageMixin
from .forms import TripPlanForm,TripPlanUpdateForm
import re
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

class HomePageView(TemplateView):
    template_name = 'home.html'

class TripPlanCreateView(CreateView):
    model = TripPlan
    form_class = TripPlanForm  # <-- 2. 'fields' O'RNIGA 'form_class' ISHLATAMIZ
    template_name = 'trip_new.html'

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
                Act as a world-class, expert travel consultant named 'Scout'. Your tone is enthusiastic, helpful, and highly detailed. Your primary goal is to deliver a complete and comprehensive itinerary.

                **Objective:** Generate a highly structured, personalized travel itinerary based on the user's preferences.

                **--- User Preferences ---**
                *   **Destination:** {destination}
                *   **Trip Duration:** {duration} days
                *   **Primary Interests:** {interests}
                *   **Budget Level:** {budget} (Interpret as: Ekonom = $, Standart = $$, Lyuks = $$$)

                **--- CRITICAL INSTRUCTION ---**
                You MUST generate a plan for the **ENTIRE duration of {duration} days**. A partial or incomplete plan is not acceptable. If the plan is for 15 days, you must provide details for all 15 days.

                **--- Strict Output Requirements ---**

                **1. Main Title (H1):**
                   - Start with a single, creative title for the trip.

                **2. Introduction (Paragraph):**
                   - Write a short, welcoming paragraph.

                **3. Day-by-Day Itinerary (Main Body):**
                   - For **every single day** from Day 1 to Day {duration}:
                     - Create a heading: `## Day X: [Creative Day Title]`
                     - Structure the day into `### Morning`, `### Afternoon`, and `### Evening`.
                     - In a bulleted list, provide: Activity, Time, Cost, Description, and a Scout's Tip.

                **4. Daily Summary Section (at the end of each day's plan):**
                   - Include a "Food Stop" and "Transport" summary for each day.

                **5. Overall Trip Summary (at the very end):**
                   - Include a "Budget Overview" and "General Tips".

                **6. Formatting Rules (Crucial):**
                   - Use Markdown extensively and consistently.
                   - Do not include any conversational filler. Start directly with the Main Title.
                """

                response = model.generate_content(prompt)

                ai_generated_plan = response.text

            except Exception as e:
                print(f"Google AI'ga so'rov yuborishda xatolik: {e}")
                ai_generated_plan = f"Reja tuzishda xatolik yuz berdi: {e}"
        form.instance.generated_plan=ai_generated_plan
        return super().form_valid(form)


class TripPlanDetailView(LoginRequiredMixin, DetailView):
    model = TripPlan
    template_name = 'trip_detail.html'
    context_object_name = 'trip'

    def get_context_data(self, **kwargs):
        # Get the default context from the parent class
        context = super().get_context_data(**kwargs)

        # Get the raw Markdown plan from the object
        plan_text = self.object.generated_plan

        # --- PARSING LOGIC STARTS HERE ---
        days = []
        # Split the text by day headings (## Day 1, ## Day 2, etc.)
        day_sections = re.split(r'\n##\s', plan_text)

        # The first part is usually the title and introduction
        if day_sections:
            header = day_sections.pop(0)
            # Split title and intro
            title_match = re.match(r'#\s*(.*)', header)
            context['plan_title'] = title_match.group(1).strip() if title_match else "Your Travel Plan"

            intro_text = re.sub(r'#\s*(.*)\n', '', header).strip()
            context['plan_introduction'] = intro_text

        # Process each day's section
        for section in day_sections:
            if section.strip():
                day_title_match = re.match(r'(Day\s*\d+.*)', section)
                day_title = day_title_match.group(1).strip() if day_title_match else "Details"
                day_content = re.sub(r'(Day\s*\d+.*)\n', '', section).strip()
                days.append({'title': day_title, 'content': day_content})

        context['days_list'] = days
        # --- PARSING LOGIC ENDS HERE ---

        return context

class TripPlanListView(LoginRequiredMixin,ListView):
    model=TripPlan
    template_name = 'my_plans.html'
    context_object_name = 'plans_list'

    def get_queryset(self):
        return TripPlan.objects.filter(user=self.request.user).order_by('-created_at')



class TripPlanUpdateView(LoginRequiredMixin,UserPassesTestMixin,SuccessMessageMixin,UpdateView):
    model=TripPlan
    form_class = TripPlanUpdateForm
    template_name = 'trip_edit.html'
    success_message = "Your travel plan was updated successfully!"

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

class TripPlanDeleteView(LoginRequiredMixin,UserPassesTestMixin,SuccessMessageMixin,DeleteView):
    model=TripPlan
    template_name = "trip_confirm_delete.html"
    success_url = reverse_lazy('my_plans_list')
    success_message = "Your travel plan was deleted successfully."



    def test_func(self):
        plan = self.get_object()
        return self.request.user == plan.user


def trip_plan_pdf_view(request, pk):

    try:
        trip_plan = TripPlan.objects.get(pk=pk)
    except TripPlan.DoesNotExist:
        return HttpResponse("Sayohat rejasi topilmadi.", status=404)

    if request.user != trip_plan.user:
        return HttpResponse("Sizda bu rejani ko'rishga ruxsat yo'q.", status=403)

    # 3. PDF uchun maxsus shablonni 'context' bilan birga HTML matniga o'giramiz
    context = {'trip': trip_plan}
    html_string = render_to_string('trip_pdf.html', context)

    # 4. WeasyPrint yordamida HTML matnidan PDF yaratamiz
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # 5. Foydalanuvchiga PDF faylni yuklab olish uchun HttpResponse qaytaramiz
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="trip_plan_{trip_plan.destination}.pdf"'
    return response