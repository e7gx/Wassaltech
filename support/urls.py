from django.urls import path
from . import views


app_name= 'support'

urlpatterns = [
    path('ticket/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.display_tickets, name='display_tickets'),
    path('ticket/detail/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/edit/<int:ticket_id>/', views.ticket_edit, name='ticket_edit'),
    path('ticket/comment/<int:ticket_id>/', views.add_comment, name='add_comment'),
]
