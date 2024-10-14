from django.shortcuts import render
from rest_framework.views import APIView
from userAuth.serializers import RegisterSerializer, UserAuthSerializer, InfoSerializer
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response

# Views for user authentication and registration

class Register(APIView):
    
    # API view for user registration.
    # Handles POST requests to create a new user account.
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # TODO: Improve error handling and logging
            print("Error: User registration failed")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Authentication(APIView):
    
    # API view for user authentication.
    # Handles POST requests to authenticate a user and return JWT tokens.
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            
            # Generate refresh and access tokens for the authenticated user
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            # TODO: Improve error handling and logging
            print("Error: Authentication failed")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Info(APIView):
    
    # API view for retrieving user information.
    # Handles POST requests to return user data.

    def post(self, request):
        serializer = InfoSerializer(data=request.data)
        return Response(serializer.data)

