# How to run

Start App Command:
```
python manage.py runserver
```

Run Tests Command:
```
python manage.py test
```

Clear and reset database:
```
python manage.py flush
```

Migrate Database:
```
python manage.py makemigrations
python manage.py migrate
```

Populate LLM-providers table:
```
python manage.py load_llm_data
```

# Backend API Documentation

This document outlines the endpoints available in the backend API, including request formats, HTTP methods, and the expected responses.

## Base URL
The base URL for all endpoints is:
```
http://localhost:8000/
```

## User Endpoints

### 1. Get User Information
**URL:** `/user/getInfo/`  
**Method:** `GET`  
**Authentication:** Requires Bearer Token  
**Description:** Retrieves the authenticated user's information.  

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Response Example:**
```json
{
  "first_name": "Ole",
  "last_name": "Normann",
  "username": "olenor",
  "email": "olenorm@ole.no",
  "country": "Norway",
  "affiliation": "University of Bergen",
  "position": "scientist",
  "field_of_study": "AI researcher"
}
```

### 2. Update User Information
**URL:** `/user/updateInfo/`  
**Method:** `POST`  
**Authentication:** Requires Bearer Token  
**Description:** Updates the user's information. Note: username, password, and email cannot be updated through this endpoint as they require 2FA.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Request Body:**
```json
{
  "first_name": "Ole",
  "last_name": "Normann",
  "country": "Norway",
  "affiliation": "University of Bergen",
  "position": "scientist",
  "field_of_study": "AI researcher"
}
```

**Response Example:**
```json
{
  "first_name": "Ole",
  "last_name": "Normann",
  "country": "Norway",
  "affiliation": "University of Bergen",
  "position": "scientist",
  "field_of_study": "AI researcher"
}
```

### 3. Authenticate User
**URL:** `/user/auth/`  
**Method:** `POST`  
**Authentication:** None required  
**Description:** Authenticates a user and provides JWT tokens.  

**Request Body:**
```json
{
  "username": "olenor",
  "password": "oleSterktPassord123"
}
```

**Response Example:**
```json
{
  "refresh": "%REFRESH_TOKEN%",
  "access": "%ACCESS_TOKEN%"
}
```

### 4. Refresh Access Token
**URL:** `/user/refresh/`  
**Method:** `POST`  
**Authentication:** None required  
**Description:** Refreshes the access token using a valid refresh token.  

**Request Body:**
```json
{
  "refresh": "%REFRESH_TOKEN%"
}
```

**Response Example:**
```json
{
  "access": "%NEW_ACCESS_TOKEN%"
}
```

### 5. Register User
**URL:** `/user/register/`  
**Method:** `POST`  
**Authentication:** None required  
**Description:** Registers a new user.  

**Request Body:**
```json
{
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
```

**Response Example:**
```json
{
  "first_name": "Ole",
  "last_name": "Normann",
  "username": "olenor",
  "email": "olenorm@ole.no",
  "country": "Norway",
  "affiliation": "University of Bergen",
  "position": "scientist",
  "field_of_study": "AI researcher"
}
```

## Chat Endpoints

### 1. Get a Conversation
**URL:** `/chat/getConversation/`  
**Method:** `GET`  
**Authentication:** Requires Bearer Token  
**Description:** Retrieves a specific conversation by ID.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Query Parameters:**
```
conversation_id: The ID of the conversation to retrieve
```

**Response Example:**
```json
{
  "id": 1,
  "title": "Research Discussion",
  "messages": [
    {
      "role": "system",
      "content": "You are BAiO, a chat bot who is an expert on biology and genomic data.",
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "role": "user",
      "content": "What are the key aspects of AI in genomics?",
      "created_at": "2024-01-15T10:01:00Z"
    },
    {
      "role": "baio",
      "content": "Key aspects include predictive analysis, data integration, etc.",
      "created_at": "2024-01-15T10:02:00Z"
    }
  ]
}
```

### 2. Get All Conversations
**URL:** `/chat/getConversations/`  
**Method:** `GET`  
**Authentication:** Requires Bearer Token  
**Description:** Retrieves all conversations for the authenticated user, ordered by creation date (newest first).

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Response Example:**
```json
[
  {
    "id": 1,
    "title": "Research Discussion",
    "created_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "title": "Project Meeting",
    "created_at": "2024-01-14T11:30:00Z"
  }
]
```

### 3. Rename a Conversation
**URL:** `/chat/renameConversation/`  
**Method:** `POST`  
**Authentication:** Requires Bearer Token  
**Description:** Renames an existing conversation.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Request Body:**
```json
{
  "conversation_id": 1,
  "title": "Updated Discussion"
}
```

**Response Example:**
```json
"Conversation successfully renamed to Updated Discussion"
```

### 4. Create a Conversation
**URL:** `/chat/createConversation/`  
**Method:** `POST`  
**Authentication:** Requires Bearer Token  
**Description:** Creates a new conversation. Automatically adds a system message defining BAiO's role.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Request Body:**
```json
{
  "title": "New Research Topic"
}
```

**Response Example:**
```json
{
  "id": 3,
  "title": "New Research Topic",
  "messages": [
    {
      "role": "system",
      "content": "You are BAiO, a chat bot who is an expert on biology and genomic data.",
      "created_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

### 5. Delete a Conversation
**URL:** `/chat/deleteConversation/`  
**Method:** `POST`  
**Authentication:** Requires Bearer Token  
**Description:** Deletes a specific conversation.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Request Body:**
```json
{
  "conversation_id": 1
}
```

**Response Example:**
```json
"Conversation with id=1 successfully deleted"
```

### 6. Add an API Key
**URL:** `/chat/addAPIKey/`  
**Method:** `POST`  
**Authentication:** Requires Bearer Token  
**Description:** Adds an OpenAI API key for the user.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Request Body:**
```json
{
  "key": "sk-...",
  "nickname": "OpenAI Key"
}
```

**Response Example:**
```json
{
  "nickname": "OpenAI Key",
  "user": 1
}
```

### 7. Get API Keys
**URL:** `/chat/getApiKeys/`  
**Method:** `GET`  
**Authentication:** Requires Bearer Token  
**Description:** Retrieves all API keys associated with the authenticated user, including their provider and associated models.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Response Example:**
```json
[
  {
    "nickname": "OpenAI Key",
    "provider": {
      "id": 1,
      "name": "OpenAI",
      "models": [
        { "id": 1, "name": "GPT-4o" },
        { "id": 2, "name": "GPT-4o mini" },
        { "id": 3, "name": "OpenAI o1-preview" },
        { "id": 4, "name": "OpenAI o1-mini" }
      ]
    },
    "created_at": "2024-10-27T14:23:35.321Z"
  },
  {
    "nickname": "Second API Key",
    "provider": {
      "id": 2,
      "name": "Custom Provider",
      "models": [
        { "id": 5, "name": "ModelX" },
        { "id": 6, "name": "ModelY" }
      ]
    },
    "created_at": "2024-10-27T15:42:13.875Z"
  }
]
```

### 8. Get LLM Providers
**URL:** `/chat/getLLMProviders/`  
**Method:** `GET`  
**Authentication:** Requires Bearer Token  
**Description:** Retrieves all LLM providers along with their associated models.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "OpenAI",
    "models": [
      { "id": 1, "name": "GPT-4o" },
      { "id": 2, "name": "GPT-4o mini" },
      { "id": 3, "name": "OpenAI o1-preview" },
      { "id": 4, "name": "OpenAI o1-mini" }
    ]
  },
  {
    "id": 2,
    "name": "OtherProvider",
    "models": [
      { "id": 5, "name": "ModelX" },
      { "id": 6, "name": "ModelY" }
    ]
  }
]
```

### 9. Send a Message
**URL:** `/chat/sendMessage/`  
**Method:** `POST`  
**Authentication:** Requires Bearer Token  
**Description:** Sends a message in a conversation and streams the AI's response.

**Request Headers:**
```
Authorization: Bearer %ACCESS_TOKEN%
```

**Request Body:**
```json
{
  "conversation_id": 1,
  "apikey_nickname": "OpenAI Key",
  "content": "What are the applications of AI in genomics?",
  "model": "gpt-4o-mini"
}
```

**Response:**
The response is streamed as plain text chunks. After completion, the response is saved as a message in the conversation.
The calls the model makes to it's functions come out in the api response like this, and should be parsed somehow on the frontend so that its not just a normal part of the message:
"called_functions:[{name:function1, args:%function_args%}, [{name:function2, args:%function_args%}, ...]"
"function_responses:[{name:function1, response:%function_response%}, [{name:function2, response:%function_response%}, ...]"


**Note:** Due to streaming response, this endpoint cannot be tested via standard REST clients. Use curl or implement streaming in your frontend:

```bash
curl -X POST http://localhost:8000/chat/sendMessage/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer %ACCESS_TOKEN%" \
     -d '{"conversation_id": %CONVERSATION_ID%, "apikey_nickname": "%APIKEY_NICKNAME%", "content": "%TEXT_PROMPT%", "model": "gpt-4o-mini"}'
