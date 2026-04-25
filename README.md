# 🧠 MoodMirror AI — Documentation

## What Is This Project?

MoodMirror AI is a two-part app:
- **Frontend** (`index.html`) — runs in the browser, handles camera, voice, and UI
- **Backend** (`server.py`) — runs Python, talks to Gemini AI, returns results

Think of it like a restaurant: the frontend is the menu/waiter, the backend is the kitchen (Gemini AI).

---

## 📁 Project Structure

```
moodmirror/
├── index.html     ← Open this in browser (the full UI)
├── server.py      ← Run this first (the AI brain)
├── .env           ← Your API keys go here
└── README.md      ← This file
```

---

## ⚡ How to Run It

### Step 1 — Install dependencies
```bash
pip install flask flask-cors google-genai python-dotenv
```

### Step 2 — Make sure your .env has your key
```
GEMINI_API_KEY=your_key_here
```

### Step 3 — Start the backend
```bash
python server.py
```
You'll see: `Running on http://localhost:5000`

### Step 4 — Open the frontend
Open `index.html` in **Google Chrome** (Chrome is required for voice features).

> ✅ The app works offline too! If the backend isn't running, it falls back to built-in suggestions.

---

## 🔌 How Frontend ↔ Backend Talks

Every feature in the app calls a backend "route" (URL endpoint).
Here's the full map:

| Feature | Frontend calls | Backend route |
|---|---|---|
| Camera emotion detect | `POST /detect-emotion` | Sends image to Gemini |
| Mood suggestions | `POST /suggestions` | Gemini suggests songs/quotes |
| AI comment on mood | `POST /ai-response` | Gemini writes response |
| Action plan | `POST /action-plan` | Gemini makes step-by-step plan |
| Voice text analysis | `POST /analyze-text` | Gemini reads the text emotion |
| Food Genie | `POST /food-suggest` | Gemini suggests food dishes |

---

## 🤖 How Gemini Is Used (server.py explained)

Your original working code was:
```python
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Hello bro!"
)
print(response.text)
```

In this project, we do the same thing but smarter:

### 1. `ask_gemini(prompt)` — plain text response
```python
def ask_gemini(prompt):
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text.strip()
```
Just like your original code. Send a string, get text back.

### 2. `ask_gemini_json(prompt)` — structured JSON response
```python
def ask_gemini_json(prompt):
    response = client.models.generate_content(model=MODEL, contents=prompt + "\nRespond ONLY in JSON.")
    text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(text)
```
We tell Gemini "respond ONLY in JSON" — then we parse it into a Python dict.
This lets us extract specific fields like `emotion`, `confidence`, `steps`, etc.

### 3. Image analysis (for camera)
```python
response = client.models.generate_content(
    model=MODEL,
    contents=[{
        "parts": [
            { "inline_data": { "mime_type": "image/jpeg", "data": base64_image } },
            { "text": "What emotion does this person have?" }
        ]
    }]
)
```
Gemini can see images! We send the camera frame as base64 and ask it to detect emotion.

---

## 🎨 Frontend Features

### Mood Detection (3 ways)
1. **Camera** — Click "Start Camera" → "Detect Mood" → Gemini analyzes your face
2. **Voice** — Tap the mic → speak how you feel → Gemini reads your emotion from words
3. **Manual** — Click any mood button (Happy, Sad, Angry, Tired, Neutral)

### Dynamic UI
The background color and accent colors change based on your mood automatically.

### Fix My Mood — Action Plan
Click "Generate Action Plan" after any mood is detected.
Gemini creates a personalized 5-step plan for that specific emotion.

### Food Genie (separate tab)
Type or speak what you're craving → Gemini suggests 4 specific dishes with emojis.
Quick chips let you tap common cravings fast.

### Voice Output
The app reads AI responses aloud using the browser's Text-to-Speech (built-in, no setup needed).

---

## 🛠 Customizing Gemini Prompts

All prompts are in `server.py`. Each route has a `prompt = f"""..."""` block.

To change how Gemini responds, just edit the prompt text. Example:
```python
# In /ai-response route, change this:
prompt = f"""
    The user's mood is: {mood}
    Write a warm message...
"""
# To be more casual:
prompt = f"""
    User is feeling {mood}. 
    Talk to them like a Gen Z best friend, use casual language.
    Keep it under 3 sentences.
"""
```

---

## ⚠️ Common Issues

| Problem | Fix |
|---|---|
| "Backend not connected" message | Run `python server.py` first |
| Voice not working | Use Google Chrome (not Firefox/Safari) |
| Camera not working | Allow camera permission when browser asks |
| Gemini responds slowly | Normal for free tier. The app still works. |
| JSON parse error | Gemini sometimes adds markdown — the code cleans this automatically |
| CORS error in browser | Make sure `flask-cors` is installed: `pip install flask-cors` |

---

## 🚀 Next Steps (Ideas to Extend)

- **Face tracking** — Add `face-api.js` in `index.html` for real-time emotion without sending to backend
- **Mood history** — Save detected moods to a JSON file or SQLite database
- **Spotify integration** — Auto-play suggested songs via Spotify API
- **More emotions** — Add: surprised, disgusted, fearful, excited
- **User accounts** — Let users log in and track mood over time
- **Deploy online** — Host backend on Railway.app or Render.com (free), frontend on Netlify

---

## 📦 Full Dependencies

```bash
pip install flask flask-cors google-genai python-dotenv
```

Your `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```