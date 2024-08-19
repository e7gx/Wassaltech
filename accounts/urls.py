from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [
    path('customer/', views.customer_account, name='customer_account'),
    path('freelancer/', views.freelancer_account, name='freelancer_account'),
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/customer/', views.profile, name='profile'),
    path('profile/freelancer/', views.profile, name='profile'),
    path('profile/<int:freelancer_id>/', views.freelancer_profile, name='freelancer_profile'),
    path('inbox/', views.inbox, name='inbox'),

]
