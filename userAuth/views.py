from django.shortcuts import render
from rest_framework.views import APIView
from userAuth.serializers import RegisterSerializer, UserAuthSerializer, InfoSerializer
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response


# Create your views here.

"""
user/auth
user/info
user/register

"""


class Register(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
             print("placeholder: user already exists")
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
##Postman works with register. Bad request with Authentication
    
class Authentication(APIView):
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if(serializer.is_valid()):
            user = serializer.validated_data
            login(request, user)
            refresh = RefreshToken.for_user(user)


            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Info(APIView):
    def post(self, request):
        serializer = InfoSerializer(data=request.data)
        return Response(serializer.data)



