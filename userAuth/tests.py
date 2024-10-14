from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

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
        
        User.objects.create_user(
            username=self.user_data['username'],
            password=self.user_data['password'],
            email="olenorm@gmail.com")
        
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

class UserInfoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.getInfo_url = '/user/getInfo/'
        self.updateInfo_url = '/user/updateInfo/'
        self.auth_url = '/user/auth/'
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

        self.client.post(self.register_url, self.user_data, format='json')
        auth_data = self.client.post(self.auth_url, {"username":self.user_data["username"],"password":self.user_data["password"]}, format='json')

        self.auth_token = auth_data.data["access"]

    def test_get_info_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        response = self.client.get(self.getInfo_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['first_name'], self.user_data['first_name'])
        self.assertEqual(response.data['last_name'], self.user_data['last_name'])
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['country'], self.user_data['country'])
        self.assertEqual(response.data['affiliation'], self.user_data['affiliation'])
        self.assertEqual(response.data['position'], self.user_data['position'])
        self.assertEqual(response.data['field_of_study'], self.user_data['field_of_study'])

    def test_get_info_invalid_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer faketoken123')
        response = self.client.get(self.getInfo_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_info_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)

        self.updated_info = {
            "first_name": "Norman",
            "last_name": "Olavstad",
            "country": "Sweden",
            "affiliation": "University of Olso",
            "position": "bio scientist",
            "field_of_study": "Biology researcher"

        }

        response1 = self.client.post(self.updateInfo_url, self.updated_info)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.get(self.getInfo_url)

        self.assertEqual(response2.data['first_name'], self.updated_info['first_name'])
        self.assertEqual(response2.data['last_name'], self.updated_info['last_name'])
        self.assertEqual(response2.data['country'], self.updated_info['country'])
        self.assertEqual(response2.data['position'], self.updated_info['position'])
        self.assertEqual(response2.data['affiliation'], self.updated_info['affiliation'])
        self.assertEqual(response2.data['field_of_study'], self.updated_info['field_of_study'])

    def test_update_info_invalid_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer faketoken123')
        self.updated_info = {
            "first_name": "Norman",
            "last_name": "Olavstad",
            "country": "Sweden",
            "affiliation": "University of Olso",
            "position": "bio scientist",
            "field_of_study": "Biology researcher"

        }
        response = self.client.post(self.updateInfo_url, self.updated_info)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_update_elevated_info(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.auth_token)
        self.updated_info = {
            "email": "hacker@scarydomain.com"
        }

        response1 = self.client.post(self.updateInfo_url, self.updated_info)
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

        response2 = self.client.get(self.getInfo_url)
        self.assertNotEqual(response2.data['email'], self.updated_info['email'])
