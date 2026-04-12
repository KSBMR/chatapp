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
    # Change 'admin' and 'password123' to what you want
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('adil', 'admin@example.com', 'password123')
        print("Admin user created successfully!")

# Run the function
try:
    create_admin()
except Exception as e:
    print(f"Admin creation skipped: {e}")