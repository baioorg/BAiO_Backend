from django.shortcuts import render
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class GetConversationsView(APIView):
    def get(self, request):
        try:
            #user id
            a = 1
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class GetConversationView(APIView):
    def get(self, request):
        try:
            #user_id and conversation_id
            a = 2
        except ObjectDoesNotExist:
            return Response({"error": "User or conversation not found"}, status=status.HTTP_404_NOT_FOUND)
        
class MessageView():
    def post(self, request):
        a = 3
