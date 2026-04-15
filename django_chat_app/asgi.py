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

# --- Add this at the very bottom ---
from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    # These will pull from Render's "Environment" tab
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    email = os.environ.get('ADMIN_EMAIL')

    if username and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            print(f"Admin {username} created!")