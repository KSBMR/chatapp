"""
Admin panel configuration for the chat application.
"""

from django.contrib import admin
from .models import Message, UserProfile


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin view for chat messages."""
    list_display = ['sender', 'receiver', 'short_message', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp', 'sender']
    search_fields = ['sender__username', 'receiver__username', 'message']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

    def short_message(self, obj):
        """Show a truncated version of the message in the list view."""
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Message Preview'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin view for user profiles."""
    list_display = ['user', 'is_online', 'last_seen', 'avatar_color']
    list_filter = ['is_online']
    search_fields = ['user__username']
    readonly_fields = ['last_seen']
