from django.urls import path
from . import views


app_name= 'support'

urlpatterns = [
    path('support/', views.support, name='support'),
]
