from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import Applicant, DocumentUploadToken
from django.urls import reverse
from django.http import HttpResponse
from .models import DocumentUploadToken
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Applicant, Document
from django.http import HttpResponseForbidden
from django import forms

class UploadDocumentForm(forms.Form):
    document_type = forms.CharField(max_length=255)
    file = forms.FileField()

def upload_document_view(request, token):
    applicant = get_object_or_404(Applicant, token=token)

    if applicant.token_expiry and applicant.token_expiry < timezone.now():
        return HttpResponseForbidden("This upload link has expired.")

    if request.method == 'POST':
        form = UploadDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = Document.objects.create(
                applicant=applicant,
                document_type=form.cleaned_data['document_type'],
                file=form.cleaned_data['file']
            )
            return render(request, 'upload_success.html', {'applicant': applicant})
    else:
        form = UploadDocumentForm()

    return render(request, 'upload_form.html', {
        'form': form,
        'applicant': applicant
    })

def upload_file(request, token):
    try:
        doc_token = DocumentUploadToken.objects.get(token=token, used=False)
    except DocumentUploadToken.DoesNotExist:
        return HttpResponse("Invalid or expired link.")

    if request.method == 'POST' and request.FILES['document']:
        file = request.FILES['document']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        
        # You can also save filename/path in a new model linked to applicant here

        doc_token.used = True
        doc_token.save()
        return HttpResponse("Thank you! Your file has been uploaded.")
    
    return render(request, 'upload_file.html', {'applicant': doc_token.applicant})


def send_upload_link(request):
    if request.method == 'POST':
        email = request.POST['email']
        note = request.POST['note']

        applicant, created = Applicant.objects.get_or_create(email=email)
        applicant.requirement_note = note
        applicant.save()

        token = DocumentUploadToken.objects.create(applicant=applicant)

        link = request.build_absolute_uri(
            reverse('upload_file', kwargs={'token': token.token})
        )

        send_mail(
            'Document Upload Request',
            f"Please upload your missing documents using this link: {link}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, f"Upload link sent to {email}.")
        return redirect('send_upload_link')  # Back to the form with success message

    return render(request, 'send_upload_link.html')

def home(request):
    return redirect('send_upload_link')
