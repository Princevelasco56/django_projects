from django.urls import path
from . import views

urlpatterns = [
    path('send-upload-link/', views.send_upload_link, name='send_upload_link'),
    path('upload/<uuid:token>/', views.upload_file, name='upload_file'),
    
]
