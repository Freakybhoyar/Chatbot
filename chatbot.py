import os
import uvicorn
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI()

LOG_FILE = "chat_log.jsonl"
session_histories: Dict[str, List[Dict[str, str]]] = {}

class UserQuery(BaseModel):
    session_id: str
    user_input: str
    user_name: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Chatbot is running!"}

@app.post("/chat")
def chat_with_llama3(query: UserQuery):
    session_id = query.session_id
    if session_id not in session_histories:
        session_histories[session_id] = []

    prompt = f"User: {query.user_input}\nBot: "
    
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "llama3", "prompt": prompt},
            stream=True
        )
        response.raise_for_status()
        
        bot_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    bot_response += json.loads(line).get("response", "")
                except json.JSONDecodeError:
                    continue
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to LLaMA API: {str(e)}")

    session_histories[session_id].append({"user": query.user_input, "bot": bot_response})
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"session_id": session_id, "user": query.user_input, "bot": bot_response}) + "\n")

    return {"bot_response": bot_response}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
