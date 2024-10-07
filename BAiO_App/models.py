from django.db import models

# Create your models here.


class User(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Usually hashed
    country = models.CharField(max_length=150, blank=True)
    affiliation = models.CharField(max_length=150, blank=True)
    position = models.CharField(max_length=150, blank=True)
    field_of_study = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def get_auth_info(self):
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password,
        }
    
    def get_profile_info(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'country': self.country,
            'affiliation': self.affiliation,
            'position': self.position,
            'field_of_study': self.field_of_study,
            'date_joined': self.date_joined,
        }
    
    def __str__(self):
        return self.username
    
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

