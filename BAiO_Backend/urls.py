"""
URL configuration for BAiO_Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from userAuth.views import *
from chat.views import *

urlpatterns = [
    path("admin/", admin.site.urls),

    # User Urls
    path("user/getInfo/",  GetInfoView.as_view()),
    path("user/updateInfo/", UpdateInfoView.as_view()),
    path("user/auth/", Authentication.as_view()),
    path("user/register/", Register.as_view(), name="register_new_user"),
    path("user/refresh/", TokenRefreshView.as_view(), name="refresh_token"),

    # Chat urls
    path("chat/getConversation/", GetConversationView.as_view()),
    path("chat/getConversations/", GetConversationsView.as_view()),
    path("chat/renameConversation/", RenameConversationView.as_view()),
    path("chat/createConversation/", CreateConversationView.as_view()),
    path("chat/deleteConversation/", DeleteConversation.as_view()),
    path("chat/addAPIKey/", AddAPIKeyView.as_view()),
    path("chat/getApiKeys/", GetAPIKeysView.as_view()),
    path("chat/getLLMProviders/", GetLLMProvidersView.as_view(), name="get_llm_providers"),
    
    # Cannot be tested through postman, use frontend or curl with this command to test. 
    # Also make sure you have a valid OpenAI API Key in settings.py before running.
    # curl -X POST http://localhost:8000/chat/sendMessage/ -H "Content-Type: application/json" -H "Authorization: Bearer %ACCESS_TOKEN%" -d "{\"conversation_id\": %CONVERSATION_ID%, \"apikey_nickname\": \"%APIKEY_NICKNAME%\", \"content\": \"%TEXT_PROMPT%\", \"model\": \"%LLM_MODEL%\"}"
    path("chat/sendMessage/", SendMessageView.as_view())


    
]


