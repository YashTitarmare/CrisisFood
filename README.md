<<<<<<< HEAD

#  CrisisFood AI

CrisisFood AI is a web-based AI chatbot built with FastAPI (Python) and Google Gemini.
It runs on any device — mobile, tablet, or desktop  with a WhatsApp-style chat interface
designed to be simple.

CrisisFood AI provides immediate, practical, and safety-first guidance on the best available
food and water options during real-life emergency and crisis situations. It is purpose-built
for the Indian context — where people face unique challenges during disasters such as limited
access to clean water, dependence on locallyavailable foods, and communication breakdowns
during in the critical situations.





## Steps

1. Add your Gemini API key in `.env` file:
   GEMINI_API_KEY=your_key_here
   Get free key → https://aistudio.google.com/app/apikey

2. Install dependencies:
   pip install -r requirements.txt

3. Run:
   uvicorn main:app --reload

4. Open browser:
   http://localhost:8000

## Versions Required
- Python 3.11
- fastapi==0.115.6
- uvicorn[standard]==0.32.1
- httpx==0.28.1
- python-dotenv==1.0.1
- jinja2==3.1.4
- python-multipart==0.0.19

=======
# CrisisFood AI 🆘

> Emergency Food & Water Safety Chatbot for India

CrisisFood AI is a web-based AI chatbot that provides real-time, safety-first food and water guidance during crisis situations. Built with FastAPI (Python) and Google Gemini API, featuring a WhatsApp-style chat interface optimized for mobile, tablet, and desktop.

![CrisisFood AI](https://img.shields.io/badge/Version-1.0.0-orange)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

---

## Features

- ** Crisis Awareness** - Handles multiple crisis types:
  - Flood / Heavy Rain
  - Blackout / Power Cut
  - Curfew / Lockdown
  - Earthquake / Disaster
  - Heatwave
  - Disease Outbreak
  - Storm / Cyclone

- **AI-Powered Responses** - Smart responses with:
  - Safe food suggestions
  - Safety warnings
  - Water guidance
  - Simple meal ideas
  - Storage tips

- **WhatsApp-Style UI** - Clean, mobile-first design with:
  - User messages on right, AI on left
  - Crisis type selector chips
  - Typing indicator
  - Colored response sections
  - Auto-scroll to latest message

- **🇮🇳 India-Focused** - Tailored for Indian context:
  - Hindi-English mixed responses
  - Indian food examples (dal, rice, chapati, etc.)
  - Maharashtra/Aurangabad context
  - Emergency contacts (112, NDRF)

---

## Project Structure

```
crisisfood_local/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── style.css            # Stylesheet
│   └── script.js            # JavaScript logic
├── .env                     # Environment variables (API key)
├── .gitignore               # Git ignore file
└── README.md                # This file
```

---

## Quick Start

### Prerequisites

- **Python 3.8+** installed
- **Google Gemini API Key** (get free at https://aistudio.google.com/)

### Step 1: Clone or Download

```bash
# If you have git
git clone <repository-url>
cd crisisfood_local

# Or download and extract the ZIP file
```

### Step 2: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the sidebar
4. Create a new API key
5. Copy the key (starts with `AIza...`)

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
# Windows
echo GEMINI_API_KEY=your_api_key_here > .env

# Linux/Mac
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Or create/edit `.env` manually:

```
GEMINI_API_KEY=AIzaSyA56ktiLZ3H18M9PQMqU3nu8alm6zvE4Z4
```

### Step 4: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install Python packages
pip install -r requirements.txt
```

### Step 5: Run the Server

```bash
# From backend directory
python main.py
```

You'll see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 6: Open in Browser

Go to: **http://localhost:8000**

---

## API Endpoints

### `GET /`

- **Description**: Serves the frontend HTML page
- **Returns**: HTML page

### `POST /chat/stream`

- **Description**: Streams AI chat responses
- **Request Body**:

```json
{
  "message": "Flood started. What food is safe?",
  "history": [
    { "role": "user", "content": "Previous message" },
    { "role": "assistant", "content": "Previous response" }
  ],
  "crisis_type": "flood"
}
```

- **Returns**: Server-Sent Events (SSE) stream

### `GET /health`

- **Description**: Health check endpoint
- **Returns**:

```json
{
  "status": "ok",
  "model": "gemini-2.0-flash",
  "api_key_configured": true
}
```

---

## 💡 Usage Tips

### Selecting Crisis Type

Click the crisis type chips at the top to set the context:

- General - For any situation
- Flood - During floods
- Blackout - During power cuts
- Curfew - During lockdowns
- Earthquake - After earthquakes
- Heatwave - During heatwaves
- Outbreak - During disease outbreaks
- Storm - During cyclones/storms

### Quick Questions

Click the suggested questions on the welcome screen for common scenarios!

### Input Tips

- Press **Enter** to send
- Hold **Shift + Enter** for new line
- Describe your situation clearly
- Include available resources (e.g., "I have rice, dal, candles, no power")

---

## Configuration

### Environment Variables

| Variable         | Required | Description                |
| ---------------- | -------- | -------------------------- |
| `GEMINI_API_KEY` | Yes      | Your Google Gemini API key |

### Gemini Model

The backend uses `gemini-2.0-flash` by default. You can change this in `backend/main.py`:

```python
GEMINI_MODEL = "gemini-2.0-flash"  # Change to your preferred model
```

---

## Troubleshooting

### "API key missing" error

1. Make sure `.env` file exists in project root
2. Verify `GEMINI_API_KEY=` is set correctly
3. Restart the server after creating/editing `.env`

### "Connection error" in UI

1. Check if server is running (`python main.py`)
2. Verify server URL is correct (http://localhost:8000)
3. Check browser console for CORS errors

### Empty responses

1. Verify your API key is valid
2. Check if you have API quota available
3. Look at server console for error messages

### Port already in use

```bash
# Find and kill the process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## Security Notes

- The chatbot provides guidance, not medical/legal advice
- Always verify critical information from official sources
- Call emergency services (112) for real emergencies

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

## This project is for educational purposes.

## 🆘 Emergency Contacts

- **National Emergency**: 112
- **NDRF**: 011-24363260
- **State Disaster Helpline**: Check your state government website

---

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- FastAPI for the excellent Python web framework
- Open source community for inspiration

---

**Made with ❤️ for India during crisis situations**

_This tool provides general guidance and is not a substitute for professional medical, legal, or official disaster management advice._
>>>>>>> bb1367e (adding the readme)
