"""
URL patterns for the chat application.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.dashboard_view, name='dashboard_root'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Main app
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('chat/<str:username>/', views.chat_view, name='chat'),
    path('profile/', views.profile_view, name='profile'),
]
