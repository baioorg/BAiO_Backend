from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
    
class UserAuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(f"Invalid credentials for {username} and {password}")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is diabled")
        return user
    
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