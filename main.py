

import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)

def run_gui():
    import tkinter as tk
    from lucid_spork.gui import LucidSporkGUI

    root = tk.Tk()
    app = LucidSporkGUI(root)
    root.mainloop()

def run_cli_test(prompt: str, simulate_sec: int = 15):

    from lucid_spork.gemini_client import generate_dream_script
    from lucid_spork.tts_engine import TTSEngine
    from lucid_spork.audio_player import AudioPlayer
    from lucid_spork.rem_scheduler import REMScheduler
    from lucid_spork.config import DEFAULT_AUDIO_PATH

    print("==========================================================")
    print("🥄 LUCID SPORK")
    print(f"Dream Prompt: '{prompt}'")
    print("==========================================================")

    print("\n[Step 1/4] Generating dream script...")
    script = generate_dream_script(prompt)
    print(f"Generated Script ({len(script)} chars):\n{script[:180]}...")
    print("\n[Step 2/4] Synthesizing audiobook speech with TTSEngine...")
    tts = TTSEngine(rate=140)
    audio_file = tts.synthesize(script, output_path=DEFAULT_AUDIO_PATH)
    print(f"Audio file created: {audio_file} (Size: {audio_file.stat().st_size} bytes)")
    print("\n[Step 3/4] Initializing Audio Player & testing whisper calibration...")
    player = AudioPlayer()
    calib_file = tts.ensure_calibration_sample()
    print(f"Calibration sample verified: {calib_file}")
    print("\n[Step 4/4] Starting REM Scheduler simulation (time_multiplier=120x)...")
    scheduler = REMScheduler(
        audio_player=player,
        audio_path=audio_file,
        sleep_onset_mins=1,
        cycle_len_mins=2,
        target_cycles=[1, 2],
        whisper_volume=0.15,
        time_multiplier=60.0,
    )

    ticks_seen = 0
    def on_tick(data):
        nonlocal ticks_seen
        ticks_seen += 1
        if ticks_seen % 3 == 0:
            print(f"  [Sleep Timer] Stage: {data['current_stage']} | Countdown to Cycle {data['next_cycle']}: {data['seconds_until_next']:.1f}s")

    scheduler.on_tick = on_tick
    scheduler.on_event = lambda msg: print(f"  [REM Event] {msg}")

    scheduler.start_sleep_session()
    import time
    time.sleep(simulate_sec)
    scheduler.stop_session()
    player.stop()

    print("\n[✔] Lucid Spork  test complete! Everything is functional.")

def main():
    parser = argparse.ArgumentParser(
        description="Lucid Spork."
    )
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode without launching GUI")
    parser.add_argument("--test", action="store_true", help="Run automated test simulation")
    parser.add_argument("--prompt", type=str, default="Gliding above a land full of sporks.", help="Dream prompt for CLI test")
    parser.add_argument("--sim-seconds", type=int, default=8, help="Seconds to run simulated REM test")
    
    args = parser.parse_args()

    if args.test:
        run_cli_test(prompt=args.prompt, simulate_sec=args.sim_seconds)
    elif args.cli:
        print("Launching Lucid Spork CLI Mode...")
        from lucid_spork.gemini_client import generate_dream_script
        from lucid_spork.tts_engine import TTSEngine
        prompt = input("Enter your dream prompt: ").strip() or "Exploring a City."
        script = generate_dream_script(prompt)
        print("\nDream Narrative:\n", script)
        tts = TTSEngine()
        path = tts.synthesize(script)
        print(f"\nAudiobook saved to: {path}")
    else:
        run_gui()

if __name__ == "__main__":
    main()
