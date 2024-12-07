from django.db import models
from django.utils import timezone

class LLMProvider(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=255)
    provider = models.ForeignKey(LLMProvider, related_name="models", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.provider.name})"


class Conversation(models.Model):
    user = models.ForeignKey('userAuth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation {self.id} with {self.user.username}'  # corrected to 'user' field


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    role = models.CharField(max_length=50, choices=[('user', 'User'), ('baio', 'BAiO'), ('system', 'System')])
    created_at = models.DateTimeField(auto_now_add=True)

class CSVFile(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='csv_files')
    file_name = models.CharField(max_length=255)
    file_path = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)


class APIKey(models.Model):
    key = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    apiProvider = models.ForeignKey(LLMProvider, on_delete=models.CASCADE, related_name='apikeys')
    url = models.URLField(max_length=255)
    user = models.ForeignKey('userAuth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'nickname'], name='unique_nicknames_per_user')
        ]
