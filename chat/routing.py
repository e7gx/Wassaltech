from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'get/chat/(?P<chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
