from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

# Serializer for user authentication
class UserAuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Authenticate user with provided username and password
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(f"Invalid credentials for {username} and {password}")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        return user

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'country',
            'affiliation',
            'position',
            'field_of_study',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, val_data):
        # Create a new user instance with validated data
        user = User.objects.create_user(
            username=val_data['username'],
            email=val_data['email'],
            password=val_data['password'],
            first_name=val_data['first_name'],
            last_name=val_data['last_name'],
            country=val_data['country'],
            affiliation=val_data['affiliation'],
            position=val_data['position'],
            field_of_study=val_data['field_of_study']
        )
        return user

# Serializer for user information
class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'country',
            'affiliation',
            'position',
            'field_of_study',
            'date_joined'
        ]
