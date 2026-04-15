import os
import sys

path = '/home/chatingapp/chatapp'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_chat_app.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()