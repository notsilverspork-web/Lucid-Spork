import time
import threading
from datetime import datetime, timedelta
from typing import List, Callable, Optional, Dict, Any
from pathlib import Path
from .config import (
    SLEEP_ONSET_MINUTES,
    CYCLE_LENGTH_MINUTES,
    TARGET_REM_CYCLES,
    FADE_IN_SECONDS,
)
from .audio_player import AudioPlayer

class REMScheduler:
    def __init__(
        self,
        audio_player: AudioPlayer,
        audio_path: Path,
        sleep_onset_mins: int = SLEEP_ONSET_MINUTES,
        cycle_len_mins: int = CYCLE_LENGTH_MINUTES,
        target_cycles: Optional[List[int]] = None,
        whisper_volume: float = 0.18,
        time_multiplier: float = 1.0,  # 1.0 for real time; 60.0 means 1 min = 1 sec (simulation)
    ):
        self.audio_player = audio_player
        self.audio_path = audio_path
        self.sleep_onset_mins = sleep_onset_mins
        self.cycle_len_mins = cycle_len_mins
        self.target_cycles = target_cycles or TARGET_REM_CYCLES
        self.whisper_volume = whisper_volume
        self.time_multiplier = time_multiplier

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.start_time: Optional[datetime] = None
        self.schedule: List[Dict[str, Any]] = []

        # Callbacks
        self.on_tick: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_event: Optional[Callable[[str], None]] = None

    def calculate_schedule(self, start_dt: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Builds the timeline of sleep stages and targeted REM audio injection windows.
        """
        start = start_dt or datetime.now()
        schedule = []
        onset_duration = timedelta(minutes=self.sleep_onset_mins)
        sleep_onset_time = start + onset_duration

        for cycle in self.target_cycles:
            # REM windows occur towards the end of each 90-minute cycle
            # In later cycles, REM is longer (20-35 mins). We target the sweet spot 70 mins into the cycle.
            rem_offset_minutes = (cycle - 1) * self.cycle_len_mins + int(self.cycle_len_mins * 0.75)
            rem_start = sleep_onset_time + timedelta(minutes=rem_offset_minutes)
            
            # Approximate total seconds from start in simulation scale
            raw_seconds_from_now = (rem_start - start).total_seconds() / self.time_multiplier

            schedule.append({
                "cycle": cycle,
                "target_time": rem_start,
                "seconds_from_now": raw_seconds_from_now,
                "triggered": False,
                "description": f"Cycle {cycle} Peak REM Infiltration (~{rem_offset_minutes / 60:.1f}h asleep)"
            })

        schedule.sort(key=lambda x: x["seconds_from_now"])
        return schedule

    def start_sleep_session(self):
        """
        Begins the bedtime tracking thread when the user hits 'I'm Going to Sleep'.
        """
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self.start_time = datetime.now()
        self.schedule = self.calculate_schedule(self.start_time)

        if self.on_event:
            self.on_event("Sleep session initiated. Lucid Spork is standing by your bedside.")

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop_session(self):
        """
        Cancels sleep session and halts any active audio.
        """
        self._running = False
        self._stop_event.set()
        self.audio_player.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.on_event:
            self.on_event("Sleep session stopped.")

    def is_running(self) -> bool:
        return self._running

    def _run_loop(self):
        elapsed_real_seconds = 0.0
        start_tick = time.time()

        while not self._stop_event.is_set():
            time.sleep(1.0)
            now_tick = time.time()
            elapsed_real_seconds = now_tick - start_tick
            effective_elapsed = elapsed_real_seconds * self.time_multiplier

            # Check next upcoming window
            upcoming = [item for item in self.schedule if not item["triggered"]]
            if not upcoming:
                if self.on_event:
                    self.on_event("All scheduled REM dream windows completed. Good morning!")
                self._running = False
                break

            next_window = upcoming[0]
            simulated_remaining_seconds = max(0.0, next_window["seconds_from_now"] - elapsed_real_seconds)
            actual_remaining_display_seconds = simulated_remaining_seconds * self.time_multiplier

            # Dispatch tick status
            if self.on_tick:
                current_stage = self._determine_current_stage(effective_elapsed)
                self.on_tick({
                    "elapsed_minutes": effective_elapsed / 60.0,
                    "current_stage": current_stage,
                    "next_cycle": next_window["cycle"],
                    "next_target_time": next_window["target_time"].strftime("%H:%M:%S"),
                    "seconds_until_next": simulated_remaining_seconds,
                    "target_cycles": len(self.schedule),
                })

            # Check if it's time to inject dream audio
            if elapsed_real_seconds >= next_window["seconds_from_now"]:
                next_window["triggered"] = True
                self._trigger_rem_audio(next_window)

    def _determine_current_stage(self, elapsed_effective_sec: float) -> str:
        elapsed_min = elapsed_effective_sec / 60.0
        if elapsed_min < self.sleep_onset_mins:
            return f"Hypnagogic Descent ({int(self.sleep_onset_mins - elapsed_min)}m remaining to sleep onset)"
        
        sleep_min = elapsed_min - self.sleep_onset_mins
        cycle_idx = int(sleep_min // self.cycle_len_mins) + 1
        pos_in_cycle = sleep_min % self.cycle_len_mins

        if pos_in_cycle < 45:
            return f"Sleep Cycle {cycle_idx}: NREM Deep Slow-Wave (Restorative)"
        elif pos_in_cycle < 65:
            return f"Sleep Cycle {cycle_idx}: Transitioning to Light Sleep"
        else:
            return f"Sleep Cycle {cycle_idx}: REM Dream Phase (High Vividness)"

    def _trigger_rem_audio(self, window_info: Dict[str, Any]):
        msg = f"🌙 Active REM window detected (Cycle {window_info['cycle']}). Whispering dream narrative..."
        if self.on_event:
            self.on_event(msg)
        try:
            self.audio_player.play(
                audio_path=self.audio_path,
                volume=self.whisper_volume,
                fade_in_sec=FADE_IN_SECONDS,
                loop=False,
            )
        except Exception as e:
            if self.on_event:
                self.on_event(f"Error during REM audio injection: {e}")
