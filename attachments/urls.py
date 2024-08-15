from django.urls import path
from . import views

urlpatterns = [
    path('attachments/', views.attachments, name='attachments'),
]
