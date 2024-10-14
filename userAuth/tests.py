from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from .models import User

# Create your tests here.
class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register_new_user')

        self.user_data = {
            "first_name": "Ole",
            "last_name": "Normann",
            "username": "olenor",
            "email": "olenorm@ole.no",
            "password": "oleSterktPassord123",
            "country": "Norway",
            "affiliation": "University of Bergen",
            "position": "scientist",
            "field_of_study": "AI researcher"

        }

    # Tests a registration with valid credentials
    def test_successful_register(self):

        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertNotIn('password', response.data)

    def test_register_already_existing_username(self):
        User.objects.create_user(
            username = "olenor",
            email = "olenor@gmail.no",
            password = "oleerkul231"
            )
        
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_already_existing_email(self):
        User.objects.create_user(
            username = "olenorma",
            email = "olenorm@ole.no",
            password = "oleerkul231"
            )
        
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        self.user_data["username"] = None
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email(self):
        self.user_data["email"] = None
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        self.user_data["password"] = None
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    
        

    
class UserLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_url = '/user/auth/'

        self.user_data = {
            "username": "olenor",
            "password": "oleSterktPassord123"
            }
        
        self.user_data_wrong_username = {
            "username": "bobby",
            "password": "oleSterktPassord123"
            }
            
        self.user_data_wrong_password = {
            "username": "olenor",
            "password": "feilpassord"
            }
        
        User.objects.create_user(self.user_data, email="olenorm@gmail.com")
        
    def test_successful_login(self):
        
        response = self.client.post(self.auth_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_wrong_username(self):
        response = self.client.post(self.auth_url, self.user_data_wrong_username, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_wrong_password(self):
        response = self.client.post(self.auth_url, self.user_data_wrong_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_fail_missing_username(self):
        self.user_data["username"] = None
        response = self.client.post(self.auth_url, self.user_data_wrong_username, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_missing_password(self):
        self.user_data["password"] = None
        response = self.client.post(self.auth_url, self.user_data_wrong_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)     