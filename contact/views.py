from django.core.mail import send_mail
from django.shortcuts import render, redirect

from .forms import ContactForm

def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['subject']
            subject = '[Fetching Tech] Contact form message: ' + topic
            from_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            send_mail(subject, message, from_email, ['konningg@gmail.com'])
            return redirect('contact_success')
    return render(request, 'contact/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contact/contact_success.html')
