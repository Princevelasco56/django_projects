from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

def send_upload_link_email(applicant):
    if not applicant.token:
        applicant.token = get_random_string(length=48)
    applicant.token_expiry = timezone.now() + timezone.timedelta(days=2)
    applicant.save()

    link = f"http://localhost:8000/upload/{applicant.token}/"

    subject = "Missing Document Submission Link"
    message = f"Hi {applicant.name},\n\nPlease upload your missing document using the link below:\n{link}\n\nThis link will expire in 48 hours."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [applicant.email])
