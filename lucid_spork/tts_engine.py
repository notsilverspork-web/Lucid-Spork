import logging
import pyttsx3
from pathlib import Path
from typing import Optional, Callable
from .config import DEFAULT_AUDIO_PATH, CALIBRATION_AUDIO_PATH

logger = logging.getLogger("LucidSpork.TTS")

class TTSEngine:
    def __init__(self, rate: int = 135, volume: float = 0.9):

        self.rate = rate
        self.volume = volume

    def synthesize(self, text: str, output_path: Optional[Path] = None, progress_cb: Optional[Callable[[str], None]] = None) -> Path:
        dest = output_path or DEFAULT_AUDIO_PATH
        dest.parent.mkdir(parents=True, exist_ok=True)

        if progress_cb:
            progress_cb("Synthesizing  dream narration...")

        logger.info(f"Synthesizing {len(text)} characters to {dest}")
        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            
            voices = engine.getProperty("voices")
            if voices:
                selected_voice = voices[0]
                for v in voices:
                    name_lower = v.name.lower()
                    if "zira" in name_lower or "eva" in name_lower or "female" in name_lower:
                        selected_voice = v
                        break
                engine.setProperty("voice", selected_voice.id)

            engine.save_to_file(text, str(dest))
            engine.runAndWait()
        finally:
            del engine

        if progress_cb:
            progress_cb("Audiobook narration ready.")
        return dest

    def ensure_calibration_sample(self) -> Path:
        """
        Generates a quick 5-second whisper calibration sample if one doesn't exist yet.
        """
        if not CALIBRATION_AUDIO_PATH.exists():
            text = "Testing earbuds volume. Adjust until this whisper is barely audible, but completely comfortable."
            self.synthesize(text, output_path=CALIBRATION_AUDIO_PATH)
        return CALIBRATION_AUDIO_PATH
