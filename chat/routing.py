from django.urls import re_path

from . import consumers
from .consumers import OnlineUserConsumer, ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<username>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r"ws/online/$", OnlineUserConsumer.as_asgi()),
]