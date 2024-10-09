from django.db import models

from userauth.models import User


# Create your models here.

class LLM(models.Model):
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title
    
class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    key = models.CharField(max_length=128)
    LargeLanguageModel = models.ForeignKey(LLM, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def get_key_info(self):
        return {
            'key': self.key,
            'date_created': self.date_created,
            'is_active': self.is_active,
        }
    
# class Message(models.Model):
#     text = models.TextField()
#     date_sent = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.title

# class UserMessage(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = Message

