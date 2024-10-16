from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Conversation, Message, APIKey
from rest_framework_simplejwt.tokens import RefreshToken
from userAuth.models import User

# Create your tests here.
class ChatTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_conversation_url = "/chat/getConversation/"
        self.get_conversations_url = "/chat/getConversations/"
        self.rename_conversation_url = "/chat/renameConversation/"
        self.create_conversation_url = "/chat/createConversation/"
        self.add_apikey_url = "/chat/addAPIKey/"
        self.auth_url = "/user/auth/"
        self.register_url = "/user/register/"

        self.user_data1 = {
            "first_name": "Ole",
            "last_name": "Normann",
            "username": "olenor",
            "email": "olenor@gmail.no",
            "password": "oleerkul231",
            "country": "Norway",
            "affiliation": "University of Bergen",
            "position": "scientist",
            "field_of_study": "AI researcher"
        }

        self.user_data2 = {
            "first_name": "Ole",
            "last_name": "Sveriemann",
            "username": "hackerman",
            "email": "hacker@gmail.no",
            "password": "superstongpass12",
            "country": "Sweden",
            "affiliation": "University of Stockholm",
            "position": "scientist",
            "field_of_study": "AI researcher"
        }

        resp1 = self.client.post(self.register_url, self.user_data1, format='json')
        resp2 = self.client.post(self.register_url, self.user_data2, format='json')

        auth_data1 = self.client.post(self.auth_url, {"username":self.user_data1["username"],"password":self.user_data1["password"]}, format='json')
        self.auth_token = auth_data1.data["access"]

        auth_data2 = self.client.post(self.auth_url, {"username":self.user_data2["username"],"password":self.user_data2["password"]}, format='json')
        self.hacker_auth_token = auth_data2.data["access"]
        

    def test_create_conversation_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        response = self.client.post(self.create_conversation_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_conversation_invalid_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer faketoken123')

        response = self.client.post(self.create_conversation_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rename_conversation_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        self.client.post(self.create_conversation_url, format='json')

        data = {
            "conversation_id": 1,
            "title": "Test"
        }

        response = self.client.post(self.rename_conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test")

    def test_rename_non_existing_conversation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        self.client.post(self.create_conversation_url, format='json')

        data = {
            "conversation_id": 10,
            "title": "Test"
        }

        response = self.client.post(self.rename_conversation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_conversations_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        self.client.post(self.create_conversation_url, format='json')
        self.client.post(self.create_conversation_url, format='json')
        self.client.post(self.create_conversation_url, format='json')

        response = self.client.get(self.get_conversations_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_conversation_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        self.client.post(self.create_conversation_url, format='json')

        
        response = self.client.get(f"{self.get_conversation_url}?conversation_id=1", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), ['id', 'title', 'messages', 'created_at'])

    def test_get_unowned_conversation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)
        self.client.post(self.create_conversation_url, format='json')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.hacker_auth_token)

        data = {
            "conversation_id": 1
        }

        response = self.client.get(f"{self.get_conversation_url}?conversation_id=1", format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # Test only works since we're not currently checking if apikeys are valid upon adding them.
    def test_add_apikey_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        data = {
            "key": "1234",
            "nickname": "Test key"
        }

        response = self.client.post(self.add_apikey_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)






        
