from django.db import models
from django.utils import timezone
# Create your models here.
class Conversation(models.Model):
    user = models.ForeignKey('userAuth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation {self.id} with {self.user1.username}'
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    role = models.CharField(max_length=50, choices=[('user', 'User'), ('baio', 'BAiO'), ('system', 'System')])
    created_at = models.DateTimeField(auto_now_add=True)
