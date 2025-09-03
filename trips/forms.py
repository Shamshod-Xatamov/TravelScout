# trips/forms.py

from django import forms
from .models import TripPlan
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML


class TripPlanForm(forms.ModelForm):
    class Meta:
        model = TripPlan
        fields = ['destination', 'duration_days', 'interests', 'budget']
        labels = {
            'destination': 'Your Amazing Destination',
            'duration_days': 'How Many Days of Adventure?',
            'interests': 'What Excites You?',
            'budget': 'Your Travel Style',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'


        self.helper.layout = Layout(
            # Har bir maydonni o'zining maxsus 'div'iga o'raymiz
            Div(
                # 'Field' yordamida maydonni va uning atributlarini belgilaymiz
                Field(
                    'destination',
                    css_class='w-full p-3 bg-yellow-100 border-2 border-yellow-500 text-black rounded-lg placeholder-gray-500',
                    placeholder='e.g., Paris, France'
                ),
                css_class='mb-6'  # Div'ning o'ziga klass
            ),
            Div(
                Field(
                    'duration_days',
                    css_class='w-full p-3 bg-green-100 border-2 border-green-500 text-black rounded-lg',
                    placeholder='e.g., 7'
                ),
                css_class='mb-6'
            ),

            Div(
                Field(
                    'interests',
                    css_class='w-full p-3 bg-blue-100 border-2 border-blue-500 text-black rounded-lg',
                    rows='4',
                    placeholder='e.g., Museums, Hiking, Local Food...'
                ),
                css_class='mb-6'
            ),
            Div(
                Field(
                    'budget',
                    css_class='w-full p-3 bg-purple-100 border-2 border-purple-500 text-black rounded-lg'
                ),
                css_class='mb-6'
            ),


            HTML('<hr class="border-gray-600 my-6">'),

            # The new, improved Submit button
            Submit(
                'submit',
                'Generate My Plan',  # Changed the text to be cleaner
                css_class='w-full bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-3 px-4 rounded-lg transition-colors text-lg'
            )
        )
        self.helper.form_tag = False

class TripPlanUpdateForm(forms.ModelForm):
    class Meta:
        model = TripPlan
        fields = ['destination', 'duration_days','interests', 'budget']
        labels = {
            'destination': 'Your Amazing Destination',
            'duration_days': 'How Many Days of Adventure?',
            'interests': 'What Excites You?',
            'budget': 'Your Travel Style',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('destination', css_class='w-full p-3 bg-slate-800 border-2 border-slate-600 text-white rounded-lg placeholder-gray-400 focus:ring-cyan-500 focus:border-cyan-500'),
            Field('duration_days', css_class='w-full p-3 bg-slate-800 border-2 border-slate-600 text-white rounded-lg placeholder-gray-400 focus:ring-cyan-500 focus:border-cyan-500'),
            Field('interests', css_class='w-full p-3 bg-slate-800 border-2 border-slate-600 text-white rounded-lg placeholder-gray-400 focus:ring-cyan-500 focus:border-cyan-500', rows='4'),
            Field('budget', css_class='w-full p-3 bg-slate-800 border-2 border-slate-600 text-white rounded-lg focus:ring-cyan-500 focus:border-cyan-500'),

        )