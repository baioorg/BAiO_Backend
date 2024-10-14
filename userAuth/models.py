from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Custom user manager to handle user creation and management
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        # Creates and saves a User with the given username, email, and password
        #
        # Args:
        #     username (str): The user's unique username
        #     email (str): The user's email address
        #     password (str, optional): The user's password
        #     **extra_fields: Additional fields to be saved in the User model
        #
        # Returns:
        #     User: The created user instance
        #
        # Raises:
        #     ValueError: If email or username is not provided
        if not email:
            raise ValueError('The Email field is required')
        if not username:
            raise ValueError('The Username field is required')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)

        # Hash the password before saving the user
        user.set_password(password)
        user.save(using=self._db)
        return user

# Custom User model with additional fields for user profile information
# Inherits from AbstractBaseUser for core user functionality and
# PermissionsMixin for Django's permission system
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=150, blank=True)
    affiliation = models.CharField(max_length=150, blank=True)
    position = models.CharField(max_length=150, blank=True)
    field_of_study = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='customer_user_permissions_set',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='customer_user_permissions_set'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def get_auth_info(self):
        # Returns a dictionary containing the user's authentication information
        #
        # Returns:
        #     dict: A dictionary with username, email, and hashed password
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password,
        }
    
    def get_profile_info(self):
        # Returns a dictionary containing the user's profile information
        #
        # Returns:
        #     dict: A dictionary with user's profile details
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
        # Returns a string representation of the user
        #
        # Returns:
        #     str: The user's username
        return self.username
