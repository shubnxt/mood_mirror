"""
MoodMirror AI — Python Backend
================================
Built on Google Gemini API (gemini-2.5-flash-preview)
Run: python server.py
Then open index.html in your browser.
"""

from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import base64
import json

load_dotenv()

# ─── Gemini Setup ──────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
MODEL = "gemini-3-flash-preview"   # fastest Gemini model

# ─── Flask App ─────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow browser requests from index.html


# ════════════════════════════════════════════════════════════════
#   HELPER: Ask Gemini
# ════════════════════════════════════════════════════════════════

def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text.strip()


def ask_gemini_json(prompt: str) -> dict:
    """
    Send a prompt asking Gemini to respond ONLY in JSON.
    Returns a parsed Python dict.
    """
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no backticks, no explanation."
    )
    text = response.text.strip()
    # Clean up any accidental markdown fences
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


# ════════════════════════════════════════════════════════════════
#   ROUTE 1: Detect Emotion from Camera Image
# ════════════════════════════════════════════════════════════════

@app.route("/detect-emotion", methods=["POST"])
def detect_emotion():
    """
    Receives a base64 image from the frontend camera.
    Asks Gemini to detect the emotion from the face.

    Request JSON:
        { "image": "data:image/jpeg;base64,..." }

    Response JSON:
        { "emotion": "happy", "confidence": 92, "message": "..." }
    """
    data = request.json
    image_data = data.get("image", "")

    # Strip the data URL prefix to get raw base64
    if "," in image_data:
        image_data = image_data.split(",")[1]

    prompt = """
    Look at this person's face and detect their emotion.
    
    Choose ONE emotion from: happy, sad, angry, tired, neutral
    
    Respond in this exact JSON format:
    {
        "emotion": "happy",
        "confidence": 88,
        "message": "You look really happy today! I can see a big smile on your face."
    }
    
    The message should be warm, friendly, and 1-2 sentences.
    Confidence is a number from 60-99.
    """

    try:
        # Gemini can analyze images — we send the image as base64
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        { "text": prompt }
                    ]
                }
            ]
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "emotion": "neutral",
            "confidence": 70,
            "message": f"Couldn't analyze image clearly. Error: {str(e)}"
        })


# ════════════════════════════════════════════════════════════════
#   ROUTE 2: Get Mood-Based Suggestions
# ════════════════════════════════════════════════════════════════

@app.route("/suggestions", methods=["POST"])
def suggestions():
    """
    Given a detected mood, returns personalized suggestions.

    Request JSON:
        { "mood": "sad" }

    Response JSON:
        { "suggestions": [ { "type": "Song", "content": "..." }, ... ] }
    """
    mood = request.json.get("mood", "neutral")

    prompt = f"""
    The user is feeling: {mood}
    
    Generate 4 personalized suggestions for them. Each suggestion should be one of:
    - A specific song recommendation
    - A motivational quote (with author)
    - A meme/GIF idea or funny suggestion
    - A fun activity idea
    
    Return this exact JSON:
    {{
        "suggestions": [
            {{ "type": "🎵 Song", "content": "Song Name – Artist" }},
            {{ "type": "💬 Quote", "content": "Quote text — Author" }},
            {{ "type": "😂 Meme", "content": "Description of a relatable meme" }},
            {{ "type": "🎯 Activity", "content": "A specific activity suggestion" }}
        ]
    }}
    
    Make them specific, warm, and actually helpful for someone feeling {mood}.
    """

    try:
        result = ask_gemini_json(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════════
#   ROUTE 3: AI Mood Comment
# ════════════════════════════════════════════════════════════════

@app.route("/ai-response", methods=["POST"])
def ai_response():
    """
    Returns a warm, empathetic AI response based on mood.

    Request JSON:
        { "mood": "happy", "type": "mood_comment" }

    Response JSON:
        { "response": "You seem full of energy today!..." }
    """
    mood = request.json.get("mood", "neutral")

    prompt = f"""
    The user's current mood is: {mood}
    
    Write a warm, friendly, empathetic message (3-4 sentences) responding to their mood.
    Be encouraging and supportive. Sound like a caring friend, not a robot.
    Don't use bullet points. Just natural conversational text.
    
    Respond in JSON:
    {{ "response": "Your message here..." }}
    """

    try:
        result = ask_gemini_json(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({"response": f"I see you're feeling {mood} today. Take care of yourself!"}), 200


# ════════════════════════════════════════════════════════════════
#   ROUTE 4: Generate Action Plan
# ════════════════════════════════════════════════════════════════

@app.route("/action-plan", methods=["POST"])
def action_plan():
    """
    Creates a personalized step-by-step plan based on mood.

    Request JSON:
        { "mood": "angry" }

    Response JSON:
        { "steps": ["Step 1...", "Step 2...", ...] }
    """
    mood = request.json.get("mood", "neutral")

    prompt = f"""
    The user is feeling: {mood}
    
    Create a practical 5-step action plan to help them feel better.
    Each step should be:
    - Short and actionable (1-2 sentences)
    - Something they can do TODAY
    - Realistic and helpful
    
    Respond in JSON:
    {{
        "steps": [
            "Step description here",
            "Step description here",
            "Step description here",
            "Step description here",
            "Step description here"
        ]
    }}
    """

    try:
        result = ask_gemini_json(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({"steps": ["Take a deep breath.", "Drink some water.", "Rest for a moment."]}), 200


# ════════════════════════════════════════════════════════════════
#   ROUTE 5: Analyze Voice/Text Input for Mood
# ════════════════════════════════════════════════════════════════

@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    """
    Analyzes user's spoken/typed text to detect mood.

    Request JSON:
        { "text": "I feel really exhausted and don't want to do anything" }

    Response JSON:
        { "emotion": "tired", "confidence": 88, "response": "..." }
    """
    text = request.json.get("text", "")

    prompt = f"""
    The user said: "{text}"
    
    Detect their emotion from this text. Choose from: happy, sad, angry, tired, neutral
    
    Also write a short empathetic response (2-3 sentences) to what they said.
    
    Respond in JSON:
    {{
        "emotion": "tired",
        "confidence": 88,
        "response": "Your empathetic response here..."
    }}
    """

    try:
        result = ask_gemini_json(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "emotion": "neutral",
            "confidence": 70,
            "response": "I hear you. Thanks for sharing how you feel."
        }), 200


# ════════════════════════════════════════════════════════════════
#   ROUTE 6: Food Genie
# ════════════════════════════════════════════════════════════════

@app.route("/food-suggest", methods=["POST"])
def food_suggest():
    """
    Suggests food based on user's craving description.

    Request JSON:
        { "query": "I want something spicy and filling" }

    Response JSON:
        {
            "foods": [
                { "emoji": "🍛", "name": "Biryani", "description": "..." },
                ...
            ],
            "description": "Overall recommendation text..."
        }
    """
    query = request.json.get("query", "")

    prompt = f"""
    The user is craving: "{query}"
    
    Suggest 4 food items that match this craving perfectly.
    Include Indian and international options where relevant.
    
    Respond in JSON:
    {{
        "foods": [
            {{
                "emoji": "🍛",
                "name": "Food Name",
                "description": "One sentence description of this dish"
            }},
            {{
                "emoji": "🌶",
                "name": "Food Name",
                "description": "One sentence description"
            }},
            {{
                "emoji": "🥘",
                "name": "Food Name",
                "description": "One sentence description"
            }},
            {{
                "emoji": "🍜",
                "name": "Food Name",
                "description": "One sentence description"
            }}
        ],
        "description": "A 2-3 sentence friendly summary of your recommendations and why they match the craving."
    }}
    
    Be specific! Don't just say 'spicy food'. Name real dishes.
    """

    try:
        result = ask_gemini_json(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "foods": [],
            "description": f"Error getting suggestions: {str(e)}"
        }), 500


# ════════════════════════════════════════════════════════════════
#   Run Server
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  MoodMirror AI — Backend Server")
    print("  Running on: http://localhost:5000")
    print("  Open index.html in your browser!")
    print("=" * 50)
    app.run(debug=True, port=5000) 