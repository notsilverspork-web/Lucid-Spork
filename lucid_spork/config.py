import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "audio_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_AUDIO_PATH = OUTPUT_DIR / "dream_incubation.wav"
CALIBRATION_AUDIO_PATH = OUTPUT_DIR / "calibration_tone.wav"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash")

# Circadian & REM timing defaults
SLEEP_ONSET_MINUTES = 20        # Time taken on average to fall asleep
CYCLE_LENGTH_MINUTES = 90       # Standard human ultradian sleep cycle
TARGET_REM_CYCLES = [3, 4, 5]   # Targeted REM cycles (approx 4.5h, 6h, 7.5h)

# Audio defaults
DEFAULT_WHISPER_VOLUME = 0.18   # Safe whisper volume (18% amplitude)
MAX_SAFE_VOLUME = 0.40          # Upper limit to prevent accidental awakenings
FADE_IN_SECONDS = 8.0           # Gradual audio fade-in so sleeper is not jolted awake
