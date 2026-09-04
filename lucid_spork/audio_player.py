import time
import threading
import logging
from pathlib import Path
from typing import Optional
import pygame
from .config import DEFAULT_WHISPER_VOLUME, MAX_SAFE_VOLUME, FADE_IN_SECONDS

logger = logging.getLogger("LucidSpork.AudioPlayer")

class AudioPlayer:
    def __init__(self):
        self._initialized = False
        self._current_volume = DEFAULT_WHISPER_VOLUME
        self._fade_thread: Optional[threading.Thread] = None
        self._stop_fade = threading.Event()
        self._init_mixer()

    def _init_mixer(self):
        if not self._initialized:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize pygame mixer: {e}")

    def set_volume(self, volume: float):
        """
        Clamps volume between 0.0 and MAX_SAFE_VOLUME to protect sleeper hearing.
        """
        clamped = max(0.0, min(float(volume), MAX_SAFE_VOLUME))
        self._current_volume = clamped
        if self._initialized:
            try:
                pygame.mixer.music.set_volume(clamped)
            except Exception:
                pass

    def get_volume(self) -> float:
        return self._current_volume

    def play(self, audio_path: Path, volume: Optional[float] = None, fade_in_sec: float = 0.0, loop: bool = False):
        self.stop()
        target_vol = volume if volume is not None else self._current_volume
        self.set_volume(target_vol)

        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            pygame.mixer.music.load(str(audio_path))
            loops = -1 if loop else 0

            if fade_in_sec > 0:
                pygame.mixer.music.set_volume(0.0)
                pygame.mixer.music.play(loops=loops)
                self._start_fade_in(target_vol, fade_in_sec)
            else:
                pygame.mixer.music.set_volume(target_vol)
                pygame.mixer.music.play(loops=loops)
        except Exception as e:
            logger.error(f"Error playing audio file {audio_path}: {e}")
            raise

    def _start_fade_in(self, target_volume: float, duration: float):
        self._stop_fade.set()
        if self._fade_thread and self._fade_thread.is_alive():
            self._fade_thread.join(timeout=0.5)

        self._stop_fade.clear()

        def fade_worker():
            steps = 30
            step_time = max(0.05, duration / steps)
            current = 0.0
            increment = target_volume / steps
            for _ in range(steps):
                if self._stop_fade.is_set():
                    break
                current += increment
                try:
                    pygame.mixer.music.set_volume(min(current, target_volume))
                except Exception:
                    break
                time.sleep(step_time)
            try:
                pygame.mixer.music.set_volume(target_volume)
            except Exception:
                pass

        self._fade_thread = threading.Thread(target=fade_worker, daemon=True)
        self._fade_thread.start()

    def stop(self):
        self._stop_fade.set()
        if self._initialized:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def is_playing(self) -> bool:
        if self._initialized:
            try:
                return pygame.mixer.music.get_busy()
            except Exception:
                return False
        return False
