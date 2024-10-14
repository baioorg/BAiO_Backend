from rest_framework import serializers

    
class GetConversationsSerializer(serializers.ModelSerializer):
    class Meta:
        
        fields = [
            'user_id'
        ]

class GetConversationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'user_id',
            'conversation_id'
        ]