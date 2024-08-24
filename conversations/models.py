from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation started at {self.started_at}'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)  # Adding a file field
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} at {self.timestamp}'
