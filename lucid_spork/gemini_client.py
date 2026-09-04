import json
import logging
import requests
from typing import Optional
from .config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger("LucidSpork.Gemini")

DREAM_SYSTEM_PROMPT = """You are the Lucid Spork Dream Architect. Your role is to write a hypnotic, deeply immersive, audiobook-style narrative designed to be whispered into a sleeper's wireless earbuds during REM sleep to steer and incubate their dream.

Guidelines:
1. Write in the second person ("You feel...", "You look up and notice...", "You begin to float...").
2. Tone: Calm, slow, soothing, rhythmic, and vivid in sensory details (sounds, lighting, textures, breeze).
3. Structure: 
   - A soft descent into the requested world.
   - Rich scenic exploration matching the user's prompt.
   - Subtle lucid awareness cues woven naturally (e.g. "You realize this world responds to your thoughts; you are lucid and in complete control.").
   - A peaceful ongoing continuation suitable for looping or fading out.
4. Length: Approximately 150-250 words (around 1.5 to 2 minutes of spoken audio).
5. Do NOT include markdown bolding, stage directions like [whisper], sound effects in brackets, or title headers. Output ONLY pure spoken narrative text ready for Text-To-Speech.
"""

def generate_dream_script(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Calls Google Gemini API to transform the user's dream idea into an audiobook dream script.
    Falls back to a tailored offline template if no API key is provided or API call fails.
    """
    key = api_key or GEMINI_API_KEY
    if not prompt or not prompt.strip():
        prompt = "Floating through a warm luminescent ocean of stars and peaceful clouds."

    if key and key.strip():
        # Try both v1beta and v1 with common model identifiers
        model_candidates = [
            ("v1beta", GEMINI_MODEL),
            ("v1beta", "gemini-1.5-flash-latest"),
            ("v1beta", "gemini-2.0-flash"),
            ("v1beta", "gemini-pro"),
            ("v1", "gemini-1.5-flash"),
        ]
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"{DREAM_SYSTEM_PROMPT}\n\nUser Dream Scenario: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.85,
                "topP": 0.95,
                "maxOutputTokens": 600,
            }
        }

        for api_ver, model_name in model_candidates:
            try:
                url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model_name}:generateContent?key={key.strip()}"
                resp = requests.post(url, headers=headers, json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            if text:
                                return text
            except Exception as e:
                logger.debug(f"Attempt with {model_name} failed: {e}")
                continue

    # Offline high-quality fallback generator
    clean_p = prompt.strip().rstrip(".")
    return (
        f"You are drifting peacefully now, weightless and calm. Before you, the world opens into {clean_p}. "
        f"Soft light washes over the horizon, painting the air in gentle, luminous shades. "
        f"You take a deep, slow breath, feeling completely safe and tranquil. Every detail around you feels alive yet tranquil. "
        f"Look down at your hands. As you look, a quiet knowing settles within your mind: this is your own dreamscape, "
        f"and you are completely aware and lucid. The breeze carries a gentle rhythm as you explore further into {clean_p}. "
        f"You have the power to shape every cloud, every shadow, and every whisper of this world. Drift onward, "
        f"lucid, empowered, and resting in total harmony."
    )
