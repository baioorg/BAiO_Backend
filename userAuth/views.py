from django.shortcuts import render
from rest_framework.views import APIView
from userAuth.serializers import RegisterSerializer, UserAuthSerializer, GetInfoSerializer, SetInfoSerializer
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

# Views for user authentication and registration

class Register(APIView):
    
    # API view for user registration.
    # Handles POST requests to create a new user account.
    
    permission_classes = [AllowAny]  # No authentication required

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
    
    permission_classes = [AllowAny]  # No authentication required

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
        
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh']
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({'access': access_token}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetInfoView(APIView):
    
    # API view for retrieving user information.
    # Handles GET requests to return user data.

    permission_classes = [IsAuthenticated]  # Requires authentication

    def get(self, request):
        user = request.user
        serializer = GetInfoSerializer(user)
   
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class UpdateInfoView(APIView):

    # API view for updating information about a user
    # Handles POST requests to update user data.

    permission_classes = [IsAuthenticated]  # Requires authentication

    def post(self, request):
        user = request.user

        restricted_fields = ['username', 'password', 'email']

        for field in restricted_fields:
            if field in request.data:
                return Response(f"Updating {field} requires 2fa", status=status.HTTP_403_FORBIDDEN)
        
        serializer = SetInfoSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateTokenView(APIView):
    """
    API view for validating JWT tokens.
    Handles POST requests to validate an access token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # This will raise an error if the token is invalid
            AccessToken(token)
            return Response(
                {'valid': True}, 
                status=status.HTTP_200_OK
            )
        except ExpiredSignatureError:
            return Response(
                {'valid': False, 'error': 'Token has expired'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except InvalidTokenError:
            return Response(
                {'valid': False, 'error': 'Token is invalid'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
