from .models import Applicant, Document
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import admin, messages
from .forms import RequestDocumentForm
from .utils import send_upload_link_email
from django.utils.crypto import get_random_string


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'token', 'token_expiry')
    actions = ['resend_upload_email']

    def resend_upload_email(self, request, queryset):
        for applicant in queryset:
            # Call your email sending logic here
            from .utils import send_upload_link_email
            send_upload_link_email(applicant)
        self.message_user(request, "Upload links resent successfully.")
    resend_upload_email.short_description = "Resend upload email"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'document_type', 'uploaded_at')
class CustomAdminSite(admin.AdminSite):
    site_header = "Document Admin Panel"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('request-document/', self.admin_view(self.request_document_view), name='request_document'),
        ]
        return custom_urls + urls

    def request_document_view(self, request):
        form = RequestDocumentForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            email = form.cleaned_data['email']
            label = form.cleaned_data['document_label']

            applicant, created = Applicant.objects.get_or_create(email=email, defaults={
                'name': email.split('@')[0],
                'token': get_random_string(length=48)
            })

            # If no token exists or expired, regenerate
            send_upload_link_email(applicant)

            messages.success(request, f"Upload link sent to {email} for: {label}")
            return redirect('admin:request_document')

        return render(request, 'admin/request_document.html', {'form': form})

# Replace default admin site
admin_site = CustomAdminSite(name='custom_admin')
admin_site.register(Applicant, ApplicantAdmin)
admin_site.register(Document, DocumentAdmin)
