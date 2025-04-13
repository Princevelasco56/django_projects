from django import forms

class RequestDocumentForm(forms.Form):
    email = forms.EmailField()
    document_label = forms.CharField(max_length=255)
