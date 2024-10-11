from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
    
class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if user and user.is_active:
            return user
        else:
            raise serializers.ValidationError('Invalid credentials')

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

    def create(self, val_data):
        user = User.objects.create(
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