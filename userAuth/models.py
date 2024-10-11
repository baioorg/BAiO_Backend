from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_info):

        user = self.model(username=username, email=email, **extra_info)
        user.set_password(password)
        if(user.is_valid()):
            user.save()

        return user

class User(AbstractBaseUser):
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

    objects= UserManager()
    
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

