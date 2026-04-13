"""
WebSocket URL routing for the chat application.

Maps WebSocket URLs to their consumer classes.
URL pattern: ws://host/ws/chat/<username>/
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Make sure this matches the path in your chat.js wsUrl
    re_path(r'ws/chat/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
