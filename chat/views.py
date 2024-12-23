from django.shortcuts import render
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, APIKey
from .serializers import *
from .baio_container.openai_container import Message_Container
from django.http import StreamingHttpResponse
from queue import Queue

# Create your views here.

class GetConversationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            conversations = Conversation.objects.filter(user=user).order_by('-created_at')
            serializer = ConversationReferenceSerializer(conversations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class GetConversationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            conversation_id = request.query_params.get('conversation_id')
            
            conversation = Conversation.objects.get(id=conversation_id, user=user)
            serializer = ConversationSerializer(conversation)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("Could not find conversation", status=status.HTTP_404_NOT_FOUND)
        
class CreateConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # Get the title from the request body, default to an empty string if not provided
        title = request.data.get('title', '')

        # Create the conversation with the user and the optional title
        conversation = Conversation.objects.create(user=user, title=title)
        
        Message.objects.create(
            conversation=conversation,
            content="You are BAiO, a chat bot who is an expert on biology and genomic data.",
            role='system'
        )

        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DeleteConversation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = DeleteConversationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        conversation_id = request.data['conversation_id']
        try:
            # Changed conversation_id to id in the query
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return Response(f"No conversation with id={conversation_id} belonging to this user was found", status=status.HTTP_404_NOT_FOUND)
        
        conversation.delete()

        return Response(f"Conversation with id={conversation_id} successfully deleted", status=status.HTTP_200_OK)

        
class RenameConversationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = RenameConversationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        conversation_id = request.data['conversation_id']
        new_title = request.data['title']

        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return Response(f"There are no conversations with id {conversation_id} connected to this user", status=status.HTTP_404_NOT_FOUND)
    
        conversation.title = new_title
        conversation.save()

        return Response(f"Conversation successfully renamed to {new_title}", status=status.HTTP_200_OK)
    
class AddAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        apikey_nickname = request.data['name']
        apiProvider_id = request.data['apiProvider']
        key = request.data['apiKey']
        
        try:
            # Retrieve the LLMProvider instance
            apiProvider = LLMProvider.objects.get(id=apiProvider_id)
            # Create the API key instance
            apiKeys = APIKey.objects.create(user=user, nickname=apikey_nickname, apiProvider=apiProvider, key=key)
            
            serializer = APIKeySerializer(apiKeys)
            return Response(f"APIKey successfully saved as {serializer.data['nickname']}", status=status.HTTP_200_OK)
        
        except LLMProvider.DoesNotExist:
            return Response(f"LLMProvider with id={apiProvider_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(f"Failed to save APIKey: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
        
        
class SendMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        conversation_id = request.data['conversation_id']
        apikey_nickname = request.data['apikey_nickname']
        model = request.data['model']

        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return Response(f"There are no conversations with id {conversation_id} connected to this user", status=status.HTTP_404_NOT_FOUND)
        
        try:
            apikey = APIKey.objects.get(nickname=apikey_nickname, user=user)
        except APIKey.DoesNotExist:
            return Response(f"There are no apikeys with nickname {apikey_nickname} connected to this user", status=status.HTTP_404_NOT_FOUND)

        Message.objects.create(
            conversation=conversation,
            content=request.data['content'],
            role='user'
        )

        message_history = Message.objects.filter(conversation=conversation).order_by('created_at')

        messages = [
            {"role": 'assistant' if message.role == 'baio' else message.role, 
             "content": message.content} 
            for message in message_history
        ]

        queue = Queue()
        message_container = Message_Container(messages, queue, apikey, model)
        message_container.start()

        full_response = []

        def response_generator():
            while True:
                try:
                    chunk = queue.get(timeout=2.0)
                    if chunk == "DONE":
                        if full_response:
                            Message.objects.create(
                                conversation=conversation,
                                content=''.join(full_response),
                                role='baio'
                            )
                        break
                    print(f"Chunk: {chunk}")
                    full_response.append(chunk)
                    yield chunk
                except Exception as e:
                    print(f"Generator error: {str(e)}")
                    continue

        return StreamingHttpResponse(response_generator(), content_type='text/plain')


class GetAPIKeysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        apikeys = APIKey.objects.filter(user=user)
        serializer = APIKeySerializer(apikeys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetLLMProvidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        providers = LLMProvider.objects.all()
        serializer = LLMProviderSerializer(providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)