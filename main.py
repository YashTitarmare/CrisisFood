import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import AsyncGenerator
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI(title="CrisisFood AI", version="1.0.0")

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Correct model (from your API access)
GEMINI_MODEL = "gemini-2.5-flash"


SYSTEM_PROMPT = """You are CrisisFood AI — an emergency food & water safety assistant specialized for India, especially Maharashtra and Aurangabad region.

Your ONLY purpose: Give immediate, practical, safety-first guidance on FOOD and WATER during crisis situations.

Crisis types you handle:
- 🌊 Flood / heavy rain
- ⚡ Blackout / power cut
- 🔒 Curfew / lockdown
- 🌍 Earthquake / disaster
- 🔥 Heatwave
- 🦠 Disease outbreak / contamination alert
- 🌪️ Storm / cyclone

Your response style:
- SHORT, direct, actionable advice
- Always prioritize SAFETY first
- Mention Indian foods (dal, rice, chapati, pickle, papad, etc.)
- Consider Maharashtra context
- Give shelf life info
- Warn what NOT to eat/drink
- Emergency: 112 (India)

Format:
1. ✅ SAFE TO EAT NOW
2. ⚠️ AVOID / DANGER
3. 💧 WATER SAFETY
4. 📦 PREP
5. 🆘 EMERGENCY TIP

Keep under 250 words.
"""

class ChatMessage(BaseModel):
    message: str
    history: list = []
    crisis_type: str = "general"


async def stream_gemini(message: str, history: list, crisis_type: str) -> AsyncGenerator[str, None]:
    print("🔥 BACKEND HIT WITH MODEL:", GEMINI_MODEL)
    if not GEMINI_API_KEY:
        yield f"data: {json.dumps({'text': '⚠️ API key missing'})}\n\n"
        return

    contents = []

    # ✅ System prompt injected safely
    contents.append({
        "role": "user",
        "parts": [{"text": SYSTEM_PROMPT}]
    })

    crisis_context = f"[Crisis: {crisis_type}] " if crisis_type != "general" else ""

    # History
    for msg in history[-10:]:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg.get("content", "")}]
        })

    # Current message
    contents.append({
        "role": "user",
        "parts": [{"text": crisis_context + message}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600,
            "topP": 0.9
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code != 200:
                yield f"data: {json.dumps({'text': f'❌ API Error {response.status_code}: {response.text[:200]}'})}\n\n"
                return

            data = response.json()

            text = ""
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    text += part.get("text", "")

            # ✅ Fake streaming for smooth UI
            for word in text.split():
                yield f"data: {json.dumps({'text': word + ' '})}\n\n"

    except httpx.TimeoutException:
        yield f"data: {json.dumps({'text': '⏱️ Timeout'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'text': f'❌ Error: {str(e)}'})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat/stream")
async def chat_stream(body: ChatMessage):
    return StreamingResponse(
        stream_gemini(body.message, body.history, body.crisis_type),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": GEMINI_MODEL,
        "api_key_set": bool(GEMINI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)