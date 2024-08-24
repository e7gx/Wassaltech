from django.urls import path
from . import views

app_name = 'chat'


urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('list/', views.chat_list, name='chat_list'),
    path('create/chat/<id_order>' , views.create_chat , name='create_chat'),
    path('get/chat/<chat_id>/', views.get_chat, name='get_chat'),
    path('send_message/<chat_id>/' , views.send_message , name='send_message'),
    path('update/chat/<chat_id>/' , views.get_chat_messages , name='get_chat_messages')
]
