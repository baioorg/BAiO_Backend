from rest_framework import serializers
from .models import Conversation, Message, APIKey

    
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'role', 'created_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
        }
        

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'messages', 'created_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'title': {'required': False}
        }

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['key', 'nickname', 'created_at']
        extra_kwargs = {
            'key': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, data):
        apikey = APIKey.objects.create(
            user = self.context['user'],
            key = data['key'],
            nickname = data['nickname']
        )

        return apikey
        


