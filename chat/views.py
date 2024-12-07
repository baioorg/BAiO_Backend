from django.shortcuts import render
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, APIKey, CSVFile
from .serializers import *
from .baio_container.openai_container_with_tools import Message_Container
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
            input_serializer = GetConversationSerializer(data=request.query_params)
            if not input_serializer.is_valid():
                return Response("Invalid request data", status=status.HTTP_400_BAD_REQUEST)
            
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

        serializer = AddAPIKeyViewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(f"Invalid request data", status=status.HTTP_400_BAD_REQUEST)
        
        name = request.data['name']  
        apiProvider_id = request.data['apiProvider_id']
        apiKey = request.data['apiKey']
        
        try:
            # Retrieve the LLMProvider instance
            if(apiProvider_id == "custom"):
                try:
                    url = request.data[url]
                except:
                    return Response(f"When using a custom apiProvider you need to specify an URL", status=status.HTTP_400_BAD_REQUEST)

                apiProvider = "custom"
            else:
                apiProvider = LLMProvider.objects.get(id=apiProvider_id)
                url = apiProvider.url
            # Create the API key instance
            apiKeys = APIKey.objects.create(user=user, nickname=name, apiProvider=apiProvider, url=url, key=apiKey)
            
            serializer = APIKeySerializer(apiKeys)
            return Response(f"APIKey successfully saved as {serializer.data['nickname']}", status=status.HTTP_201_CREATED)
        
        except LLMProvider.DoesNotExist:
            return Response(f"LLMProvider with id={apiProvider_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(f"Failed to save APIKey: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class DeleteAPIKeyView(APIView):
    permission_clauses = [IsAuthenticated]
    def post(self, request):
        user = request.user

        serializer = DeleteAPIKeySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        apikey_id = request.data['apikey_id']
        try:
            # Changed conversation_id to id in the query
            apikey = APIKey.objects.get(apikey_id=apikey_id, message__conversation__user=user)
        except APIKey.DoesNotExist:
            return Response(f"No API keys with id={apikey_id} belonging to this user was found", status=status.HTTP_404_NOT_FOUND)
        
        apikey.delete()

        return Response(f"API key with id={apikey_id}, nickname={apikey.nickname} successfully deleted", status=status.HTTP_200_OK)
        
        
class SendMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = SendMessageViewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response("Invalid request data", status=status.HTTP_400_BAD_REQUEST)
        
        conversation_id = request.data['conversation_id']
        apikey_id = request.data['apikey_id']
        model = request.data['model']

        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return Response(f"There are no conversations with id {conversation_id} connected to this user", status=status.HTTP_404_NOT_FOUND)
        
        try:
            apikey_object = APIKey.objects.get(id=apikey_id, user=user)
        except APIKey.DoesNotExist:
            return Response(f"There are no apikeys with id {apikey_id} connected to this user", status=status.HTTP_404_NOT_FOUND)

        url = apikey_object.url
        apikey = apikey_object.key

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
        message_container = Message_Container(messages=messages, 
                                              queue=queue, 
                                              apikey=apikey, 
                                              model=model, 
                                              conversation_id=conversation_id, 
                                              url=url
                                              )
        message_container.start()

        full_response = []

        def response_generator():
            while True:
                try:
                    chunk = queue.get(timeout=15.0)
                    if chunk == "DONE":
                        if full_response:
                            Message.objects.create(
                                conversation=conversation,
                                content=''.join(full_response),
                                role='baio'
                            )
                        break
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

class GetCSVFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        user = request.user

        try:
            csvfile = CSVFile.objects.get(id=file_id, message__conversation__user=user)
        except:
            return Response(f"CSV File with id {file_id} does not exist", status=status.HTTP_404_NOT_FOUND)
        
        file_path = csvfile.file_path.path
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=csvfile.file_name)
        
