from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_create_offer, name='notifications'),
]
