from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('freelancers/', views.admin_check_freelancers, name='admin_check_freelancers'),
    path('tickets/all', views.admin_tickets, name='admin_tickets'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('customers/', views.admin_check_customers, name='customers'),
    path('customer/<int:pk>/', views.customer_profile, name='customer_profile'),
]
