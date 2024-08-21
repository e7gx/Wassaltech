from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('freelancers/', views.admin_check_freelancers, name='analytics'),
    path('tickets/', views.admin_tickets, name='tickets'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
]
