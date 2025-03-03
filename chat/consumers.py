import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from chat.models import Message

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"
#
#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))
#

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.me = self.scope["user"]

        self.other_user = await sync_to_async(self.get_user_by_username, thread_sensitive=True)(self.other_username)
        if not self.other_user or self.other_user == self.me:
            await self.close()
            return

        self.room_name = f"chat_{min(self.me.id, self.other_user.id)}_{max(self.me.id, self.other_user.id)}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await sync_to_async(self.get_chat_messages, thread_sensitive=True)()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'message': msg.message,
                'from_user': msg.from_user.username,
                'receiver_user': msg.receiver_user.username,
                'timestamp': str(msg.timestamp),
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        msg_obj = await sync_to_async(self.create_message, thread_sensitive=True)(self.me, self.other_user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.message,
                'from_user': self.me.username,
                'receiver_user': self.other_user.username,
                'timestamp': str(msg_obj.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # Sinxron metodlarni alohida yozib, sync_to_async bilan chaqiramiz
    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_chat_messages(self):
        return list(
            Message.objects.filter(
                from_user__in=[self.me, self.other_user],
                receiver_user__in=[self.me, self.other_user]
            )
            .select_related("from_user", "receiver_user")  # Bog'liq maydonlarni oldindan yuklash
            .order_by("timestamp")
        )

    def create_message(self, from_user, to_user, message):
        return Message.objects.create(
            from_user=from_user,
            receiver_user=to_user,
            message=message
        )

online_users = set()

class OnlineUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Foydalanuvchi WebSocket-ga ulanadi"""
        if self.scope["user"].is_authenticated:
            self.group_name = "online_users"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # Foydalanuvchini online userlar ro'yxatiga qo'shamiz
            online_users.add(self.scope["user"].username)
            await self.notify_users()

    async def disconnect(self, close_code):
        """Foydalanuvchi WebSocket-ni tark etadi"""
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

            # Foydalanuvchini offline qilib qo'yamiz
            online_users.discard(self.scope["user"].username)
            await self.notify_users()

    async def notify_users(self):
        """Barcha foydalanuvchilarga kim online ekanligini jo‘natish"""
        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "update_users",
                "users": list(online_users)  # Set ni listga o‘giramiz
            }
        )

    async def update_users(self, event):
        """Frontend-ga WebSocket orqali ma'lumot jo‘natish"""
        await self.send(text_data=json.dumps({
            "users": event["users"]
        }))
