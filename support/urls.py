from django.urls import path
from . import views


app_name= 'support'

urlpatterns = [
    path('ticket/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.display_tickets, name='display_tickets'),
]
