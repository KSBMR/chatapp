"""
Views for the chat application.

Views:
- register_view   : New user registration
- login_view      : User login
- logout_view     : User logout
- dashboard_view  : Main page showing all users
- chat_view       : One-to-one chat page with a specific user
- profile_view    : User profile page
"""

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Max

from .forms import RegisterForm, LoginForm
from .models import Message, UserProfile


# ─────────────────────────────────────────────
# Helper: Avatar colors for new users
# ─────────────────────────────────────────────
AVATAR_COLORS = [
    '#6366f1', '#8b5cf6', '#ec4899', '#ef4444',
    '#f97316', '#eab308', '#22c55e', '#14b8a6',
    '#3b82f6', '#06b6d4',
]


def get_or_create_profile(user):
    """Get or create a UserProfile for the given user."""
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'avatar_color': random.choice(AVATAR_COLORS)}
    )
    return profile


# ─────────────────────────────────────────────
# Authentication Views
# ─────────────────────────────────────────────

def register_view(request):
    """Handle new user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a profile with a random avatar color
            UserProfile.objects.create(
                user=user,
                avatar_color=random.choice(AVATAR_COLORS)
            )
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account is ready.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'chat/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Mark user as online
            profile = get_or_create_profile(user)
            profile.is_online = True
            profile.save()
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'chat/login.html', {'form': form})


def logout_view(request):
    """Handle user logout and mark them offline."""
    if request.user.is_authenticated:
        profile = get_or_create_profile(request.user)
        profile.is_online = False
        profile.last_seen = timezone.now()
        profile.save()
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
# Main Application Views
# ─────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """
    Dashboard: shows all users except the current one.
    Also shows the last message and unread count for each conversation.
    """
    current_user = request.user
    # Get all users except self, ordered by username
    all_users = User.objects.exclude(id=current_user.id).order_by('username')

    # Build a list of users with conversation metadata
    user_list = []
    for user in all_users:
        profile = get_or_create_profile(user)
        # Get the last message in the conversation
        last_msg = Message.objects.filter(
            Q(sender=current_user, receiver=user) |
            Q(sender=user, receiver=current_user)
        ).order_by('-timestamp').first()

        # Count unread messages from this user
        unread_count = Message.objects.filter(
            sender=user,
            receiver=current_user,
            is_read=False
        ).count()

        user_list.append({
            'user': user,
            'profile': profile,
            'last_message': last_msg,
            'unread_count': unread_count,
        })

    # Sort: users with recent messages appear first
    user_list.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    context = {
        'user_list': user_list,
        'current_user': current_user,
        'current_profile': get_or_create_profile(current_user),
    }
    return render(request, 'chat/dashboard.html', context)


@login_required
def chat_view(request, username):
    """
    One-to-one chat page between the current user and another user.
    Loads chat history and marks messages as read.
    """
    current_user = request.user
    other_user = get_object_or_404(User, username=username)

    # Can't chat with yourself
    if other_user == current_user:
        return redirect('dashboard')

    # Mark all messages from other_user as read
    Message.objects.filter(
        sender=other_user,
        receiver=current_user,
        is_read=False
    ).update(is_read=True)

    # Load full conversation history
    conversation = Message.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by('timestamp')

    # Get all users for the sidebar
    all_users = User.objects.exclude(id=current_user.id).order_by('username')
    user_list = []
    for user in all_users:
        profile = get_or_create_profile(user)
        last_msg = Message.objects.filter(
            Q(sender=current_user, receiver=user) |
            Q(sender=user, receiver=current_user)
        ).order_by('-timestamp').first()
        unread_count = Message.objects.filter(
            sender=user,
            receiver=current_user,
            is_read=False
        ).count()
        user_list.append({
            'user': user,
            'profile': profile,
            'last_message': last_msg,
            'unread_count': unread_count,
        })

    user_list.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    context = {
        'other_user': other_user,
        'other_profile': get_or_create_profile(other_user),
        'conversation': conversation,
        'current_user': current_user,
        'current_profile': get_or_create_profile(current_user),
        'user_list': user_list,
    }
    return render(request, 'chat/chat.html', context)


@login_required
def profile_view(request):
    """View and update the current user's profile."""
    profile = get_or_create_profile(request.user)
    return render(request, 'chat/profile.html', {
        'profile': profile,
        'current_user': request.user,
    })
