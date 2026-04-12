import os
from django.core.asgi import get_asgi_application

# 1. Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_chat_app.settings')

# 2. Initialize the ASGI application early to prevent AppRegistryNotReady
django_asgi_app = get_asgi_application()

# 3. NOW you can import the rest of your channels code
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing 

application = ProtocolTypeRouter({
    # Use the application we initialized in step 2
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})