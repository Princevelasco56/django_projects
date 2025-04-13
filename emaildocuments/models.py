from django.db import models
import uuid

class Applicant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    
class DocumentUploadToken(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.email} - {self.token}"

def upload_to(instance, filename):
    identifier = instance.applicant.email.replace('@', '_').replace('.', '_')
    return f'applicants/{identifier}/{filename}'

class Document(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.name} - {self.document_type}"
