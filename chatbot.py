from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import requests
import json
from datetime import datetime
from typing import Dict, List
from typing import Optional

app = FastAPI()

# Dictionary to track conversation history for active sessions
session_histories: Dict[str, List[Dict[str, str]]] = {}

LOG_FILE = "chat_log.jsonl"

# Request model
class UserQuery(BaseModel):
    session_id: str  # Unique session identifier
    user_input: str
    user_name: Optional[str] = None  # Optional user name for personalization

def log_conversation(user_input, bot_response, session_id):
    """
    Logs conversation with session tracking.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user": user_input,
        "bot": bot_response
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def build_prompt(user_input, session_id, user_name=None):
    """
    Build a prompt including conversation context for the current session.
    """
    history = session_histories.get(session_id, [])
    prompt = ""
    for turn in history:
        prompt += f"User: {turn['user']}\nBot: {turn['bot']}\n"
    if user_name:
        prompt += f"{user_name}: {user_input}\nBot: "
    else:
        prompt += f"User: {user_input}\nBot: "
    return prompt

@app.post("/chat")
def chat_with_llama3(query: UserQuery):
    session_id = query.session_id

    # Ensure session history exists
    if session_id not in session_histories:
        session_histories[session_id] = []

    # Build prompt with session context
    prompt = build_prompt(query.user_input, session_id, query.user_name)

    try:
        # Send request to LLaMA 3 API
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "llama3", "prompt": prompt},
            stream=True
        )
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to LLaMA API: {str(e)}")

    # Process streamed response
    full_response = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    full_response += data["response"]
                if data.get("done", False):
                    break
            except json.JSONDecodeError:
                continue

    bot_response = full_response.strip()

    # Save conversation in session history
    session_histories[session_id].append({
        "user": query.user_input,
        "bot": bot_response
    })

    # Log the conversation
    log_conversation(query.user_input, bot_response, session_id)

    return {"bot_response": bot_response}

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    session_histories[session_id] = []

    try:
        while True:
            user_input = await websocket.receive_text()
            prompt = build_prompt(user_input, session_id)

            try:
                response = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={"model": "llama3", "prompt": prompt},
                    stream=True
                )
                response.raise_for_status()
            except requests.RequestException as e:
                await websocket.send_text(f"Error: {str(e)}")
                continue

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "response" in data:
                            full_response += data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

            bot_response = full_response.strip()

            session_histories[session_id].append({
                "user": user_input,
                "bot": bot_response
            })

            await websocket.send_text(bot_response)

    except WebSocketDisconnect:
        del session_histories[session_id]