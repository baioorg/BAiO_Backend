from django.db import models
from django.utils import timezone
# Create your models here.
class Conversation(models.Model):
    user1 = models.ForeignKey('userAuth.User', on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user1.username}\'s conversation'
    
class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_role = models.CharField(max_length=4, choices=ROLE_CHOICES)
    content = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
