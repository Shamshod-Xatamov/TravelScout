from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm
from django.conf import settings

def support_view(request):
    if request.method == 'POST':

        form = ContactForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']


            full_message = f"Message from: {name} ({email})\n\n{message_body}"


            send_mail(
                f"Support Request: {subject}",
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! We will get back to you shortly.")
            return redirect('support:contact')

    else:

        form = ContactForm()

    return render(request, 'support/contact.html', {'form': form})