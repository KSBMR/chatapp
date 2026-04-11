"""
WebSocket URL routing for the chat application.

Maps WebSocket URLs to their consumer classes.
URL pattern: ws://host/ws/chat/<username>/
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # When the frontend connects to ws://.../ws/chat/john/,
    # it's routed to ChatConsumer with username='john'
    re_path(r'ws/chat/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
