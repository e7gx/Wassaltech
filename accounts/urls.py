from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [
    path('customer/', views.customer_account, name='customer_account'),
    path('freelancer/', views.freelancer_account, name='freelancer_account'),
    path('logout/', views.logout_view, name='logout_view'),
    path('inbox/', views.inbox, name='inbox'),

]
