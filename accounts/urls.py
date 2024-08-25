from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [
    path('customer/', views.customer_account, name='customer_account'),
    path('freelancer/', views.freelancer_account, name='freelancer_account'),
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/customer/', views.customer_view_profile, name='customer_view_profile'),
    path('profile/freelancer/', views.freelancer_view_profile, name='profile'),
    path('profile/<int:freelancer_id>/', views.freelancer_profile, name='freelancer_profile'),
    path('edit/profile/<int:user_id>/' , views.Edit_Profile , name='Edit_Profile'),
]
