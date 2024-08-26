from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('freelancers/', views.admin_check_freelancers, name='admin_check_freelancers'),
    path('tickets/all', views.admin_tickets, name='admin_tickets'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('customers/', views.admin_check_customers, name='customers'),
    path('customer/<int:pk>/', views.customer_profile, name='customer_profile'),
    path('freelancer-edit/<int:pk>/', views.edit_freelancer_profile, name='edit_freelancer_profile'),
    path('payment/', views.admin_payment, name='admin_payment'),
    path('payment-deposit/', views.admin_deposit, name='admin_deposit'),
    path('admin_deposit_payment/<int:pk>/', views.admin_deposit_payment, name='admin_deposit_payment'),
]
