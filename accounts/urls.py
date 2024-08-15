from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [
    path('customer/login', views.customer_login, name='customer_login'),
    path('customer/signup', views.customer_signup, name='customer_signup'),
    path('Freelancer/login', views.freelancer_login, name='freelancer_login'),
    path('Freelancer/signup', views.freelancer_signup, name='freelancer_signup'),
]
