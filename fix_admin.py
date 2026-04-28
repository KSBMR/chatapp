import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_chat_app.settings')
django.setup()

from django.contrib.auth.models import User

# Use the exact credentials from your screenshot
username = 'adil'
email = 'shahbaz@gmail.com'
password = 'adil12345'

try:
    User.objects.filter(username=username).delete()
    User.objects.create_superuser(username, email, password)
    print("--- ADMIN ACCOUNT CREATED SUCCESSFULLY ---")
except Exception as e:
    print(f"--- ERROR: {e} ---")