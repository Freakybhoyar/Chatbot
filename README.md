# AI-Powered Smart Chatbot with FastAPI and LLaMA 3

This is a simple AI-powered chatbot built using FastAPI and LLaMA 3. The chatbot accepts user queries via a POST request and generates intelligent, context-aware responses using LLaMA 3.

## Features

- **POST Endpoint**: Accepts user queries and returns AI-generated responses.
- **Conversation Logging**: Logs all conversations with timestamps and session tracking.
- **Context Awareness**: Maintains conversation context within the same session.
- **Personalization**: Remembers the user's name for personalized responses.

## How to Use

### **1️⃣ Open the API Documentation**
The chatbot is live at the following link:
http://34.72.140.161:8080/docs

### **2️⃣ Test the Chatbot**
#### ** Using Swagger UI**
1. Click on **`POST /chat`**.
2. Click **"Try it out"**.
3. Enter your details in the request body:
   ```json
   {
     "session_id": "your_unique_session_id",
     "user_input": "Your_input_query",
     "user_name": "Your_name"
   }

