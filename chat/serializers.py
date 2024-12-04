from rest_framework import serializers
from .models import Conversation, Message, APIKey, LLMProvider, Model, CSVFile

    
class MessageSerializer(serializers.ModelSerializer):
    csv_files = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'role', 'created_at', 'csv_files']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def get_csv_files(self, obj):
        return CSVFileReferenceSerializer(obj.csv_files, many=True).data
        

class ConversationSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'messages', 'created_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'title': {'required': False}
        }

    def get_messages(self, obj):
        messages = obj.messages.filter(role__in=['user', 'baio'])

        return MessageSerializer(messages, many=True).data


class CSVFileReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVFile
        fields = ['id', 'file_name', 'created_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
        }



class ConversationReferenceSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'message_count', 'created_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def get_message_count(self, obj):
        return obj.messages.count()

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ['id', 'name']

class LLMProviderSerializer(serializers.ModelSerializer):
    models = ModelSerializer(many=True)  

    class Meta:
        model = LLMProvider
        fields = ['id', 'name', 'models']



class APIKeySerializer(serializers.ModelSerializer):
    provider = LLMProviderSerializer(source='apiProvider', read_only=True)

    class Meta:
        model = APIKey
        fields = ['key', 'nickname', 'provider', 'created_at']
        extra_kwargs = {
            'key': {'write_only': True},
            'created_at': {'read_only': True}
        }


    def create(self, data):
        apikey = APIKey.objects.create(
            user = self.context['user'],
            key = data['key'],
            nickname = data['nickname'],
            apiProvider=data['apiProvider']
        )

        return apikey
    
class RenameConversationSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True, max_length=255)

class DeleteConversationSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField(required=True)
