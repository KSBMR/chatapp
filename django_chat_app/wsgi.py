# import os
# import sys

# path = '/home/chatingapp/chatapp'
# if path not in sys.path:
#     sys.path.append(path)

# os.environ['DJANGO_SETTINGS_MODULE'] = 'django_chat_app.settings'

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()


import os
import sys
from django.core.wsgi import get_wsgi_application

path = '/home/chatingapp/chatapp'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_chat_app.settings'

application = get_wsgi_application()

# --- PASSWORD RESET LOGIC START ---
# This runs on Render every time the app deploys
try:
    from django.contrib.auth.models import User
    
    # Get values from your Render Env Vars, or use defaults
    username = os.environ.get('ADMIN_USERNAME', 'adil')
    email = os.environ.get('ADMIN_EMAIL', 'shahbaz@gmail.com')
    password = os.environ.get('ADMIN_PASSWORD', '12345')

    # Delete the old user to prevent "Already Exists" errors
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    
    # Create the fresh superuser
    User.objects.create_superuser(username, email, password)
    print("✅ SUCCESS: Admin password has been reset to 12345")
except Exception as e:
    print(f"❌ ERROR resetting admin: {e}")
# --- PASSWORD RESET LOGIC END ---