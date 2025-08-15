import os

from groq import Groq
from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.urls import reverse_lazy
from .models import TripPlan

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.messages.views import SuccessMessageMixin
from .forms import TripPlanForm,TripPlanUpdateForm
import re
import requests
import json
try:
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        client = Groq(api_key=groq_api_key)
    else:
        client = None
        print("WARNING: GROQ_API_KEY not found in .env file. AI features will be disabled.")
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

class HomePageView(TemplateView):
    template_name = 'home.html'

class TripPlanCreateView(CreateView):
    model = TripPlan
    form_class = TripPlanForm
    template_name = 'trip_new.html'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user

        destination = form.cleaned_data.get('destination')
        duration = form.cleaned_data.get('duration_days')
        interests = form.cleaned_data.get('interests')
        budget = form.cleaned_data.get('budget')

        final_plan_text = f"Error: Could not generate itinerary for {destination}."

        if client:
            try:
                # --- Yagona, KUCHAYTIRILGAN PROMPT ---
                # Endi biz AI'dan ham marshrut, ham JSON formatidagi geolokatsiyalarni bitta so'rovda olamiz.
                unified_prompt = f"""
                Act as a world-class, expert travel consultant named 'Scout'. Your tone is enthusiastic, helpful, and highly detailed.
                Your entire response MUST be in English and formatted in Markdown.

                **USER PREFERENCES:**
                - Destination: {destination}
                - Duration: {duration} days
                - Interests: {interests}
                - Budget: {budget} (Interpret this as: Economy = $, Standard = $$, Luxury = $$$)

                **--- ITINERARY STRUCTURE (MUST be followed exactly) ---**
                # [A creative and exciting title for the trip]
                [A short, 2-3 sentence welcoming paragraph.]
                ---
                ## Day 1: [A creative title for Day 1]
                ### Morning
                - **Activity:** [Description of an activity at a specific place]
                - **Time:** [Estimated time]
                - **Cost:** [Estimated cost]
                - **Description:** [A short description]
                - **Scout's Tip:** [A helpful tip]
                (...repeat this structure for all {duration} days...)
                ---
                ## Overall Trip Summary
                ### Budget Overview
                - [A rough total estimated cost.]
                ### General Tips
                - [2-3 general tips.]

                **--- CRITICAL FINAL REQUIREMENT ---**
                At the VERY END of your entire response, after everything else, add a special section that starts with the exact marker `LOCATIONS_JSON:`.
                This section must contain a valid, minified JSON array of objects. Each object represents a specific, plottable location mentioned in the itinerary and must have three keys: "name" (string), "lat" (number), and "lng" (number). Provide your best-effort, approximate coordinates.

                Example:
                LOCATIONS_JSON:[{{"name":"Eiffel Tower","lat":48.8584,"lng":2.2945}},{{"name":"Louvre Museum","lat":48.8606,"lng":2.3376}},{{"name":"Le Procope","lat":48.8530,"lng":2.3390}}]
                """

                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": unified_prompt}],
                    model="llama3-70b-8192",  # Yoki kuchliroq model
                    temperature=0.7,
                )
                final_plan_text = completion.choices[0].message.content
                print("INFO: Sayohat rejasi va geolokatsiyalar muvaffaqiyatli generatsiya qilindi.")

            except Exception as e:
                print(f"ERROR: AI'ga so'rov yuborishda xatolik: {e}")
                final_plan_text = f"An error occurred while generating the plan: {e}"

        form.instance.generated_plan = final_plan_text
        return super().form_valid(form)



class TripPlanUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = TripPlan
    form_class = TripPlanUpdateForm
    template_name = 'trip_edit.html'
    success_message = "Your travel plan was updated successfully!"

    def form_valid(self, form):
        # Yaratishdagi logikani deyarli to'liq takrorlaymiz
        destination = form.cleaned_data.get('destination')
        duration = form.cleaned_data.get('duration_days')
        interests = form.cleaned_data.get('interests')
        budget = form.cleaned_data.get('budget')

        final_plan_text = f"Error: Could not regenerate itinerary for {destination}."

        if client:
            try:
                # --- Xuddi o'sha yagona, KUCHAYTIRILGAN PROMPT ---
                unified_prompt = f"""
                Act as a world-class, expert travel consultant named 'Scout'. Your tone is enthusiastic, helpful, and highly detailed.
                Your entire response MUST be in English and formatted in Markdown.

                **USER PREFERENCES:**
                - Destination: {destination}
                - Duration: {duration} days
                - Interests: {interests}
                - Budget: {budget} (Interpret this as: Economy = $, Standard = $$, Luxury = $$$)

                **--- ITINERARY STRUCTURE (MUST be followed exactly) ---**
                # [A creative and exciting title for the trip]
                [A short, 2-3 sentence welcoming paragraph.]
                ---
                ## Day 1: [A creative title for Day 1]
                ### Morning
                - **Activity:** [Description of an activity at a specific place]
                - **Time:** [Estimated time]
                - **Cost:** [Estimated cost]
                - **Description:** [A short description]
                - **Scout's Tip:** [A helpful tip]
                (...repeat this structure for all {duration} days...)
                ---
                ## Overall Trip Summary
                ### Budget Overview
                - [A rough total estimated cost.]
                ### General Tips
                - [2-3 general tips.]

                **--- CRITICAL FINAL REQUIREMENT ---**
                At the VERY END of your entire response, after everything else, add a special section that starts with the exact marker `LOCATIONS_JSON:`.
                This section must contain a valid, minified JSON array of objects. Each object represents a specific, plottable location mentioned in the itinerary and must have three keys: "name" (string), "lat" (number), and "lng" (number). Provide your best-effort, approximate coordinates.

                Example:
                LOCATIONS_JSON:[{{"name":"Eiffel Tower","lat":48.8584,"lng":2.2945}},{{"name":"Louvre Museum","lat":48.8606,"lng":2.3376}},{{"name":"Le Procope","lat":48.8530,"lng":2.3390}}]
                """

                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": unified_prompt}],
                    model="llama3-70b-8192",
                    temperature=0.7,
                )
                final_plan_text = completion.choices[0].message.content
                print("INFO: Sayohat rejasi va geolokatsiyalar muvaffaqiyatli yangilandi.")

            except Exception as e:
                print(f"ERROR: AI'ga so'rov yuborishda xatolik: {e}")
                final_plan_text = f"An error occurred while generating the plan: {e}"

        form.instance.generated_plan = final_plan_text
        return super().form_valid(form)

    def test_func(self):
        plan = self.get_object()
        return self.request.user == plan.user


class TripPlanDetailView(LoginRequiredMixin, DetailView):
    model = TripPlan
    template_name = 'trip_detail.html'
    context_object_name = 'trip'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        full_response_text = self.object.generated_plan

        # Boshlang'ich qiymatlar
        itinerary_text = full_response_text
        locations_for_map = []

        # --- 1. MATNDAN JSON QISMINI AJRATIB OLISH VA PARSE QILISH (YANGI USUL) ---
        try:
            # `LOCATIONS_JSON:` markerini qidiramiz
            if "LOCATIONS_JSON:" in full_response_text:
                parts = full_response_text.split("LOCATIONS_JSON:", 1)
                itinerary_text = parts[0].strip()  # Reja matni
                locations_json_str = parts[1].strip()  # JSON satri

                # AI'dan kelgan JSON satrini to'g'ridan-to'g'ri Python list'iga o'tkazamiz
                # Endi Geoapify yoki boshqa tashqi servisga ehtiyoj yo'q!
                locations_for_map = json.loads(locations_json_str)
                print(f"INFO: {len(locations_for_map)} ta lokatsiya JSON'dan muvaffaqiyatli o'qildi.")

            else:
                print("WARNING: 'LOCATIONS_JSON' marker AI javobida topilmadi.")

        except json.JSONDecodeError as e:
            print(f"ERROR: AI'dan kelgan JSON'ni o'qishda xatolik: {e}")
        except Exception as e:
            print(f"ERROR: Lokatsiyalarni ajratib olishda kutilmagan xatolik: {e}")

        # --- 2. MATN QISMINI SARLAVHA, KIRISH VA KUNLARGA AJRATISH (O'ZGARISHSIZ QOLADI) ---
        context['plan_title'] = "Your Travel Plan"
        context['plan_introduction'] = ""
        context['days_list'] = []

        try:
            day_sections = re.split(r'\n##\s+', itinerary_text)
            if day_sections:
                header_part = day_sections.pop(0).strip()
                header_lines = header_part.split('\n', 1)
                context['plan_title'] = header_lines[0].replace('#', '').strip()
                if len(header_lines) > 1:
                    context['plan_introduction'] = header_lines[1].strip()

                days_list = []
                for section in day_sections:
                    if section.strip():
                        parts = section.split('\n', 1)
                        day_title = parts[0].strip()
                        day_content = parts[1].strip() if len(parts) > 1 else ""
                        days_list.append({'title': day_title, 'content': day_content})
                context['days_list'] = days_list
        except Exception as e:
            print(f"ERROR: Reja matnini parsing qilishda xatolik: {e}")
            context['days_list'] = [{'title': 'Full Itinerary', 'content': itinerary_text}]

        # Sarlavha va kirish qismini tozalash (o'zgarishsiz qoladi)
        if context.get('plan_title'):
            context['plan_title'] = context['plan_title'].replace('**', '').strip()
        if context.get('plan_introduction'):
            intro_lines = context['plan_introduction'].split('\n')
            cleaned_lines = [
                line for line in intro_lines
                if not line.strip().startswith('===') and not line.strip().startswith('---')
            ]
            context['plan_introduction'] = "\n".join(cleaned_lines).strip()

        # --- 3. YAKUNIY MA'LUMOTLARNI KONTEKSTGA QO'SHISH ---
        context['locations_json'] = json.dumps(locations_for_map)  # Bu endi to'g'ridan-to'g'ri AI'dan kelgan ma'lumot
        context['google_maps_api_key'] = os.environ.get('GOOGLE_MAPS_API_KEY')

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
        if client:
            try:

                prompt = f"""
                                Act as a world-class, expert travel consultant named 'Scout'. Your tone is enthusiastic, helpful, and highly detailed. Your primary goal is to deliver a complete and comprehensive itinerary.
                                code
                                Code
                                **Objective:** Generate a highly structured, personalized travel itinerary based on the user's preferences provided below.

                                            **--- User Preferences ---**
                                            *   **Destination:** {destination}
                                            *   **Trip Duration:** {duration} days
                                            *   **Primary Interests:** {interests}
                                            *   **Budget Level:** {budget} (Interpret this as: Ekonom = $, Standart = $$, Lyuks = $$$)

                                            **--- CRITICAL INSTRUCTIONS (Must be followed exactly) ---**
                                            1.  **Full Duration:** You MUST generate a plan for the **ENTIRE duration of {duration} days**.
                                            2.  **Location Highlighting:** For every specific, real-world, plottable location name (a museum, monument, specific restaurant, park, or station), you MUST wrap it in double asterisks.
                                                - **DO NOT** make the labels like "Activity:", "Cost:", or "Food Stop:" bold. Only the names themselves.
                                                - **Correct Example:** "Activity: Visit the **Eiffel Tower**."
                                                - **Incorrect Example:** "**Activity:** Visit the Eiffel Tower."

                                            **--- Strict Output Requirements ---**

                                            **1. Main Title (H1):**
                                               - Start with a single, creative, and exciting title for the entire trip.

                                            **2. Introduction (Paragraph):**
                                               - Write a short (2-3 sentences), welcoming paragraph that builds excitement.

                                            **3. Day-by-Day Itinerary (Main Body):**
                                               - For **every single day** from Day 1 to Day {duration}:
                                                 - Create a heading: `## Day X: [Creative Day Title]`
                                                 - Structure the day into `### Morning`, `### Afternoon`, and `### Evening`.
                                                 - In a bulleted list, provide:
                                                   - **Activity:** A specific activity, featuring highlighted locations like **[Location Name]**.
                                                   - **Time:** An estimated time allocation (e.g., "9:00 AM - 12:00 PM").
                                                   - **Cost:** An estimated cost in local currency and USD.
                                                   - **Description:** A brief, compelling description.
                                                   - **Scout's Tip:** A practical, insider tip.

                                            **4. Daily Summary Section (at the end of each day's plan):**
                                               - **Food Stop:** Suggest one specific, highlighted restaurant: **[Restaurant Name]**.
                                               - **Transport:** Recommend the best mode of transport for that day's plan.

                                            **5. Overall Trip Summary (at the very end):**
                                               - **Budget Overview:** A rough total estimated cost for activities.
                                               - **General Tips:** 2-3 general tips for the destination.

                                            **6. Formatting Rules (Crucial):**
                                               - Use Markdown extensively and consistently.
                                               - **DO NOT** include any conversational filler like "Here is your plan:". Start directly with the Main Title. The entire output must be only the itinerary itself.
                                            **--- FINAL REQUIREMENT ---**
                                At the very end of your entire response, after everything else, add a section that starts with `LOCATIONS_LIST:` followed by a comma-separated list of all the plottable location names you mentioned. Do not use bolding or any other formatting in this list.
                                Example:
                                LOCATIONS_LIST: Eiffel Tower, Louvre Museum, Le Procope, Champ de Mars"""
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    model="llama3-8b-8192",
                )
                ai_generated_plan = chat_completion.choices[0].message.content
            except Exception as e:
                print(f"Error calling Groq API: {e}")
                ai_generated_plan = f"An error occurred while generating the plan: {e}"

        form.instance.generated_plan = ai_generated_plan
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