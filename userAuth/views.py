from django.shortcuts import render
from rest_framework.views import APIView
from userAuth.serializers import RegisterSerializer, UserAuthSerializer, InfoSerializer

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
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)
    
class Authentication(APIView):
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            update_last_login(None, user)
            return Response({'message': 'Login successful!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Info(APIView):
    def post(self, request):
        serializer = InfoSerializer(data=request.data)
        return Response(serializer.data)



