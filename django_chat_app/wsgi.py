"""
WSGI config for django_chat_app project.
Note: For real-time features, use ASGI (asgi.py) with Daphne instead.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_chat_app.settings')

application = get_wsgi_application()
