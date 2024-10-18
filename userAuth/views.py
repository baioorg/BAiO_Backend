from django.shortcuts import render
from rest_framework.views import APIView
from userAuth.serializers import RegisterSerializer, UserAuthSerializer, InfoSerializer
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


# Create your views here.


from rest_framework.permissions import AllowAny

class Register(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Authentication(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Info(APIView):
    permission_classes = [IsAuthenticated]  # Ensures the user must be authenticated to access this view

    def get(self, request):
        # Use request.user to get the authenticated user based on the token
        user = request.user
        serializer = InfoSerializer(user)  # Serialize the user object
        return Response(serializer.data)


