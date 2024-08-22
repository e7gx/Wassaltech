

from django.urls import path
from . import views

app_name = 'chat'


urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('create/chat/<id_order>' , views.create_chat , name='create_chat'),
    path('get/chat/<chat_id>/', views.get_chat, name='get_chat'),
    path('send_message/<chat_id>/' , views.send_message , name='send_message')
]
