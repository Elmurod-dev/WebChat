from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model, TextField, ForeignKey, CASCADE, ImageField, DateTimeField


class CustomUser(AbstractUser):
    avatar = ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username


class Message(Model):
    message = TextField()
    from_user = ForeignKey(CustomUser, on_delete=CASCADE, related_name='sent_messages')
    receiver_user = ForeignKey(CustomUser, on_delete=CASCADE, related_name='received_messages')
    timestamp = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']  # Xabarlarni vaqt bo‘yicha tartiblash (eski > yangi)

    def __str__(self):
        return f"{self.from_user} → {self.receiver_user}: {self.message[:30]}"



