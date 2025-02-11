# AI-Powered Smart Chatbot with FastAPI and LLaMA 3

This is a simple AI-powered chatbot built using FastAPI and LLaMA 3. The chatbot accepts user queries via a POST request and generates intelligent, context-aware responses using LLaMA 3.

## Features

- **POST Endpoint**: Accepts user queries and returns AI-generated responses.
- **Conversation Logging**: Logs all conversations with timestamps and session tracking.
- **Context Awareness**: Maintains conversation context within the same session.
- **Personalization**: Remembers the user's name for personalized responses.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn requests
