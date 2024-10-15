from django.shortcuts import render
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer
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
            serializer = ConversationSerializer(conversations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class GetConversationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            conversation_id = request.data['conversation_id']
            
            conversation = Conversation.objects.get(id=conversation_id, user=user)
            serializer = ConversationSerializer(conversation)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        
class CreateConversationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        conversation = Conversation.objects.create(user=user)
        Message.objects.create(
            conversation=conversation,
            content="You are BAiO, a chat bot who is an expert on biology and genomic data.",
            role='system'
        )
        serializer = ConversationSerializer(conversation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        
class RenameConversationView(APIView):

    permission_clauses = [IsAuthenticated]

    def post(self, request):
        user = request.user
        conversation_id = request.data['conversation_id']

        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return Response(f"There are no conversations with id {conversation_id} connected to this user", status=status.HTTP_404_NOT_FOUND)
    
        serializer = ConversationSerializer(conversation, data=request.data, partial=True)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        
class SendMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        conversation_id = request.data['conversation_id']
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return Response(f"There are no conversations with id {conversation_id} connected to this user", status=status.HTTP_404_NOT_FOUND)

        user_prompt = Message.objects.create(
            conversation=conversation,
            content=request.data['content'],
            role='user'
        )

        message_history = Message.objects.filter(conversation=conversation).order_by('created_at')

        messages = [
            {"role": message.role, "content": message.content} for message in message_history
        ]

        # Create a Queue to communicate between the thread and the generator
        queue = Queue()

        # Start the threaded LLM container with messages and queue
        message_container = Message_Container(messages, queue)
        message_container.start()

        # Streaming generator
        def response_generator():
            while True:
                chunk = queue.get()
                if chunk is None:
                    break
                yield chunk

        return StreamingHttpResponse(response_generator(), content_type='text/plain')

