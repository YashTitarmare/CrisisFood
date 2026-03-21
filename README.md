
#  CrisisFood AI

CrisisFood AI is a web-based AI chatbot built with FastAPI (Python) and Google Gemini.
It runs on any device — mobile, tablet, or desktop  with a WhatsApp-style chat interface
designed to be simple.

CrisisFood AI provides immediate, practical, and safety-first guidance on the best available
food and water options during real-life emergency and crisis situations. It is purpose-built
for the Indian context — where people face unique challenges during disasters such as limited
access to clean water, dependence on locallyavailable foods, and communication breakdowns
during in the critical situations.


Crisis Type	Guidance Provided
Flood / Heavy Rain	Contamination risks, safe dry foods, water purification
Blackout / Power Cut	Fridge safety timelines, no-cook food options
Lockdown	Dry stock recommendations, shelf-stable Indian foods
Earthquake / Disaster	Emergency kit foods, water safety, minimal cooking
Heatwave	Hydration foods, electrolytes, items to avoid
Disease Outbreak	Contamination prevention, safe preparation methods
Storm / Cyclone	Pre-storm stocking, what to eat during and after


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

