"""
ASGI config for django_chat_app project.

It exposes the ASGI callable as a module-level variable named ``application``.
Django Channels uses this to handle both HTTP and WebSocket connections.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_chat_app.settings')

# ProtocolTypeRouter routes connections based on their type:
# - 'http'       → Standard Django views
# - 'websocket'  → Django Channels consumers (real-time chat)
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
