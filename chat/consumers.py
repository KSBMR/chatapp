"""
WebSocket Consumer for real-time chat.

How it works:
1. When a user opens a chat page, JavaScript creates a WebSocket connection.
2. The consumer's connect() method is called — it joins a "room" group.
3. When a user sends a message, receive() is called.
4. The message is saved to the database, then broadcast to everyone in the room group.
5. Each connected client's websocket_message() method is triggered, and the message
   is sent to their WebSocket connection (the browser).
6. When the user closes the page, disconnect() cleans up the group membership.

Room naming: We use a sorted pair of usernames to create a unique, consistent
room name for any two users, regardless of who initiated the chat.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, UserProfile


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Asynchronous WebSocket consumer that handles real-time messaging
    between two users.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is established.
        - Identifies the two users in the chat
        - Creates a unique group name for their conversation
        - Adds this connection to the group
        - Marks the current user as online
        """
        self.sender_username = self.scope['user'].username
        self.receiver_username = self.scope['url_route']['kwargs']['username']

        # Create a consistent room name by sorting usernames alphabetically
        # This ensures user_A chatting with user_B uses the same room as user_B chatting with user_A
        users_sorted = sorted([self.sender_username, self.receiver_username])
        self.room_name = f"chat_{'_'.join(users_sorted)}"
        self.room_group_name = f"chat_{self.room_name}"

        # Reject unauthenticated connections
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        # Join the chat room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Mark user as online
        await self.set_online_status(self.scope['user'], True)

        # Notify the room that this user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.sender_username,
                'is_online': True,
            }
        )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection closes.
        - Removes this connection from the group
        - Marks user as offline
        """
        # Mark user as offline
        if self.scope['user'].is_authenticated:
            await self.set_online_status(self.scope['user'], False)
            # Notify room that user went offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'username': self.sender_username,
                    'is_online': False,
                }
            )

        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when the server receives a message from the WebSocket (browser).
        - Parses the JSON message
        - Saves it to the database
        - Broadcasts it to everyone in the room group
        """
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if not message_text:
            return  # Ignore empty messages

        sender = self.scope['user']

        # Save message to database (sync DB call wrapped for async)
        saved_message = await self.save_message(
            sender_username=self.sender_username,
            receiver_username=self.receiver_username,
            message_text=message_text,
        )

        # Broadcast the message to the room group
        # This triggers websocket_message() for every connected client in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',          # Maps to the chat_message() method below
                'message': message_text,
                'sender': self.sender_username,
                'timestamp': saved_message['timestamp'],
                'message_id': saved_message['id'],
            }
        )

    async def chat_message(self, event):
        """
        Called when a message is broadcast to the group.
        Sends the message to the WebSocket (browser).
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    async def user_status(self, event):
        """
        Called when a user's online status changes.
        Sends the status update to the WebSocket (browser).
        """
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'username': event['username'],
            'is_online': event['is_online'],
        }))

    # ─────────────────────────────────────────────
    # Database helpers (sync → async wrappers)
    # ─────────────────────────────────────────────

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message_text):
        """Save a message to the database and return its data."""
        try:
            sender = User.objects.get(username=sender_username)
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return None

        msg = Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=message_text,
        )
        return {
            'id': msg.id,
            'timestamp': msg.timestamp.strftime('%H:%M'),
        }

    @database_sync_to_async
    def set_online_status(self, user, is_online):
        """Update user's online status in the database."""
        try:
            profile = UserProfile.objects.get(user=user)
            profile.is_online = is_online
            if not is_online:
                profile.last_seen = timezone.now()
            profile.save()
        except UserProfile.DoesNotExist:
            pass
