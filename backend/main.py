"""
CrisisFood AI - Backend
FastAPI server with Google Gemini API integration
"""
import os
import json
import asyncio
import httpx
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import AsyncGenerator, List
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="CrisisFood AI",
    version="1.0.0",
    description="Emergency food & water safety chatbot for India"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/style.css")
async def serve_css():
    """Serve CSS file"""
    css_path = FRONTEND_DIR / "style.css"
    with open(css_path, "r", encoding="utf-8") as f:
        from fastapi.responses import Response
        return Response(content=f.read(), media_type="text/css")


@app.get("/script.js")
async def serve_js():
    """Serve JavaScript file"""
    js_path = FRONTEND_DIR / "script.js"
    with open(js_path, "r", encoding="utf-8") as f:
        from fastapi.responses import Response
        return Response(content=f.read(), media_type="application/javascript")

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"

# System prompt for CrisisFood AI
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
4. 📦 PREP & STORAGE
5. 🆘 EMERGENCY TIP

Keep under 250 words. Use simple Hindi-English mixed language (Hinglish) if helpful."""


class ChatMessage(BaseModel):
    message: str
    history: List[dict] = []
    crisis_type: str = "general"


DEMO_RESPONSES = {
    "flood": """1. ✅ SAFE TO EAT NOW
    - Sealed packaged food (biscuits, chips, namkeen)
    - Canned food if unopened
    - Cooked rice/dal in clean containers
    - Dry fruits, peanuts, roasted chana

    2. ⚠️ AVOID / DANGER
    - Food touched by flood water
    - Open/loose food exposed to contamination
    - Raw vegetables from flooded garden
    - Milk packets if seal is broken

    3. 💧 WATER SAFETY
    - BOIL all water for 10+ minutes before drinking
    - Use chlorine tablets (1 per liter)
    - Avoid tap/municipal water until declared safe
    - Use bottled water if available

    4. 📦 PREP & STORAGE
    - Store drinking water in clean containers
    - Keep emergency ration for 3-5 days
    - Rice, dal, biscuits = best survival food

    5. 🆘 EMERGENCY TIP
    - Call 112 for rescue · NDRF: 011-24363260""",

    "blackout": """1. ✅ SAFE TO EAT NOW
    - Frozen food (if freezer stays closed)
    - Refrigerated food < 4 hours
    - Canned/packaged food
    - Dry fruits, biscuits, chapati with pickle

    2. ⚠️ AVOID / DANGER
    - Raw meat/fish left outside fridge > 2 hrs
    - Milk products left unrefrigerated
    - Cooked rice/dal > 4 hours without heat

    3. 💧 WATER SAFETY
    - Municipal supply usually fine
    - Boil if using borewell/groundwater
    - Store extra water for drinking

    4. 📦 PREP & STORAGE
    - Ice packs in cooler box
    - Freeze water bottles for later use
    - Keep torch + batteries ready

    5. 🆘 EMERGENCY TIP
    - Don't open fridge/freezer unnecessarily
    - Food stays safe 4 hrs in closed fridge""",

    "general": """1. ✅ SAFE TO EAT NOW
    - Dal, rice, chapati with sabzi
    - Curd, buttermilk (if fresh)
    - Seasonal fruits (banana, apple)
    - Peanuts, chana, murmura

    2. ⚠️ AVOID / DANGER
    - Food past expiry date
    - Uncooked/undercooked meat
    - Food with unusual smell/color
    - Leftover food kept > 4 hours

    3. 💧 WATER SAFETY
    - Use filtered/boiled water
    - Check RO/tank cleaning date
    - Carry own water when traveling

    4. 📦 PREP & STORAGE
    - Stock 3 days dry ration
    - Rice, dal, biscuits, peanuts
    - Carry torch, water bottle always

    5. 🆘 EMERGENCY TIP
    - In crisis: prioritize water over food
    - Call 112 for emergency help"""
}


async def stream_gemini(message: str, history: List[dict], crisis_type: str) -> AsyncGenerator[str, None]:
    """Stream responses from Gemini API or demo mode"""
    
    # Use demo mode if no API key or key is placeholder
    if not GEMINI_API_KEY or GEMINI_API_KEY in ("YOUR_API_KEY_HERE", "demo_mode", ""):
        # Demo mode - use canned responses
        demo_key = crisis_type if crisis_type in DEMO_RESPONSES else "general"
        text = DEMO_RESPONSES[demo_key]
        
        # Simulate streaming
        for word in text.split():
            yield f"data: {json.dumps({'text': word + ' '})}\n\n"
            await asyncio.sleep(0.02)
        
        yield f"data: {json.dumps({'done': True})}\n\n"
        return

    contents = []

    # System prompt
    contents.append({
        "role": "user",
        "parts": [{"text": SYSTEM_PROMPT}]
    })

    # Crisis context
    crisis_context = f"[Crisis Type: {crisis_type}] " if crisis_type != "general" else ""

    # Conversation history (last 10 messages)
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
                error_msg = f"API Error {response.status_code}: {response.text[:200]}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                return

            data = response.json()
            text = ""
            
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    text += part.get("text", "")

            # Stream word by word for smooth UI
            for word in text.split():
                yield f"data: {json.dumps({'text': word + ' '})}\n\n"

    except httpx.TimeoutException:
        yield f"data: {json.dumps({'error': 'Request timed out. Please try again.'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': f'Error: {str(e)}'})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the frontend"""
    html_path = FRONTEND_DIR / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/chat/stream")
async def chat_stream(body: ChatMessage):
    """Streaming chat endpoint"""
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
    """Health check endpoint"""
    return {
        "status": "ok",
        "model": GEMINI_MODEL,
        "api_key_configured": bool(GEMINI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT)]
    )
