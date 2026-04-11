"""
Chat application models.

Models:
- Message: Stores chat messages between users
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    """
    Represents a chat message between two users.
    
    Fields:
        sender    - The user who sent the message
        receiver  - The user who receives the message
        message   - The text content of the message
        timestamp - When the message was sent
        is_read   - Whether the receiver has read the message
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Sender'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Receiver'
    )
    message = models.TextField(verbose_name='Message')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='Sent At')
    is_read = models.BooleanField(default=False, verbose_name='Read')

    class Meta:
        ordering = ['timestamp']  # Oldest messages first
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.message[:40]}"

    @staticmethod
    def get_conversation(user1, user2):
        """
        Returns all messages exchanged between two users,
        ordered from oldest to newest.
        """
        return Message.objects.filter(
            sender=user1, receiver=user2
        ) | Message.objects.filter(
            sender=user2, receiver=user1
        ).order_by('timestamp')


class UserProfile(models.Model):
    """
    Extends the built-in User model with additional fields.
    Tracks online/offline status.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    avatar_color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text='Hex color for avatar background'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
