import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path

from .config import (
    DEFAULT_AUDIO_PATH,
    DEFAULT_WHISPER_VOLUME,
    MAX_SAFE_VOLUME,
    GEMINI_API_KEY,
)
from .gemini_client import generate_dream_script
from .tts_engine import TTSEngine
from .audio_player import AudioPlayer
from .rem_scheduler import REMScheduler

# Theme Colors
BG_DARK = "#0d0c18"
BG_CARD = "#17152b"
BG_INPUT = "#211f3d"
ACCENT_VIOLET = "#8b5cf6"
ACCENT_CYAN = "#38bdf8"
ACCENT_GREEN = "#10b981"
ACCENT_RED = "#f43f5e"
TEXT_WHITE = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class LucidSporkGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lucid Spork - Algorithmic Dream Control")
        self.root.geometry("920x860")
        self.root.minsize(840, 720)
        self.root.configure(bg=BG_DARK)

        # Core Engines
        self.tts = TTSEngine(rate=135)
        self.player = AudioPlayer()
        self.scheduler = None

        self.dream_script_text = ""
        self.generated_audio_path = DEFAULT_AUDIO_PATH
        self.is_session_active = False

        self._build_ui()
        self._init_tts_sample()

    def _init_tts_sample(self):
        # Pre-cache calibration sample in background
        threading.Thread(target=self.tts.ensure_calibration_sample, daemon=True).start()

    def _build_ui(self):
        # Header Bar
        header = tk.Frame(self.root, bg=BG_DARK, pady=12, padx=20)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="🥄 LUCID SPORK",
            font=("Segoe UI", 22, "bold"),
            fg=TEXT_WHITE,
            bg=BG_DARK,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header,
            text="Control ur dreams",
            font=("Segoe UI", 10),
            fg=ACCENT_CYAN,
            bg=BG_DARK,
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))
        container = tk.Frame(self.root, bg=BG_DARK, padx=20, pady=5)
        container.pack(fill=tk.BOTH, expand=True)

        card_dream = tk.Frame(container, bg=BG_CARD, padx=16, pady=14, relief=tk.FLAT)
        card_dream.pack(fill=tk.X, pady=6)

        c1_title = tk.Label(
            card_dream,
            text="1. DREAM ARCHITECT (Google Gemini AI)",
            font=("Segoe UI", 12, "bold"),
            fg=ACCENT_VIOLET,
            bg=BG_CARD,
        )
        c1_title.pack(anchor="w")

        # API Key row
        key_frame = tk.Frame(card_dream, bg=BG_CARD)
        key_frame.pack(fill=tk.X, pady=(6, 4))
        
        tk.Label(key_frame, text="Gemini API Key:", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=GEMINI_API_KEY)
        self.api_key_entry = tk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            font=("Segoe UI", 9),
            show="*",
            bg=BG_INPUT,
            fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT,
        )
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        # Dream Prompt Input
        tk.Label(
            card_dream,
            text="Describe the dream you want to experience:",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_WHITE,
            bg=BG_CARD,
        ).pack(anchor="w", pady=(6, 2))

        self.prompt_entry = tk.Text(
            card_dream,
            height=3,
            font=("Segoe UI", 10),
            bg=BG_INPUT,
            fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=10,
            pady=8,
        )
        self.prompt_entry.pack(fill=tk.X)
        self.prompt_entry.insert(
            tk.END,
            "Flying through aa land full of sporks.",
        )

        btn_gen_frame = tk.Frame(card_dream, bg=BG_CARD)
        btn_gen_frame.pack(fill=tk.X, pady=(8, 0))

        self.btn_generate = tk.Button(
            btn_gen_frame,
            text="✨ Maake your dream audio (Gemini + TTS)",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_VIOLET,
            fg=TEXT_WHITE,
            activebackground="#7c3aed",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._on_generate_clicked,
        )
        self.btn_generate.pack(side=tk.LEFT)

        self.gen_status_lbl = tk.Label(
            btn_gen_frame,
            text="Ready to synthesize your dream.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        self.gen_status_lbl.pack(side=tk.LEFT, padx=12)

        # === CARD 2: AUDIOBOOK PRIMING & VOLUME CALIBRATION ===
        card_audio = tk.Frame(container, bg=BG_CARD, padx=16, pady=14)
        card_audio.pack(fill=tk.X, pady=6)

        c2_title = tk.Label(
            card_audio,
            text="2. PRIMING & EARBUDS CALIBRATION",
            font=("Segoe UI", 12, "bold"),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
        )
        c2_title.pack(anchor="w")

        desc_lbl = tk.Label(
            card_audio,
            text="Put in your wireless earbuds. Listen 1-2 times while awake to prime your mind. Adjust whisper volume so it's faint enough not to wake you up.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            wraplength=840,
            justify=tk.LEFT,
        )
        desc_lbl.pack(anchor="w", pady=(2, 6))

        # Audio Controls Row
        audio_ctrl_row = tk.Frame(card_audio, bg=BG_CARD)
        audio_ctrl_row.pack(fill=tk.X, pady=4)

        self.btn_play_preview = tk.Button(
            audio_ctrl_row,
            text="🎧 Play Dream Audiobook Preview",
            font=("Segoe UI", 9, "bold"),
            bg=BG_INPUT,
            fg=TEXT_WHITE,
            activebackground="#2e2b52",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._toggle_preview_audio,
        )
        self.btn_play_preview.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_test_whisper = tk.Button(
            audio_ctrl_row,
            text="🔊 Test Earbuds Whisper Level",
            font=("Segoe UI", 9),
            bg=BG_INPUT,
            fg=TEXT_WHITE,
            activebackground="#2e2b52",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._play_calibration_test,
        )
        self.btn_test_whisper.pack(side=tk.LEFT, padx=(0, 15))

        # Volume slider
        tk.Label(audio_ctrl_row, text="Earbuds Volume:", font=("Segoe UI", 9, "bold"), fg=TEXT_WHITE, bg=BG_CARD).pack(side=tk.LEFT)
        self.vol_var = tk.DoubleVar(value=DEFAULT_WHISPER_VOLUME * 100)
        self.vol_slider = ttk.Scale(
            audio_ctrl_row,
            from_=1.0,
            to=MAX_SAFE_VOLUME * 100,
            orient=tk.HORIZONTAL,
            variable=self.vol_var,
            command=self._on_volume_changed,
            length=160,
        )
        self.vol_slider.pack(side=tk.LEFT, padx=8)

        self.vol_lbl = tk.Label(
            audio_ctrl_row,
            text=f"{int(DEFAULT_WHISPER_VOLUME * 100)}% (Whisper)",
            font=("Segoe UI", 9),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
        )
        self.vol_lbl.pack(side=tk.LEFT)

        # === CARD 3: BEDTIME LAUNCH & REM TIMING ENGINE ===
        card_sleep = tk.Frame(container, bg=BG_CARD, padx=16, pady=14)
        card_sleep.pack(fill=tk.BOTH, expand=True, pady=6)

        c3_title = tk.Label(
            card_sleep,
            text="3. PURE TIMING REM SCHEDULER",
            font=("Segoe UI", 12, "bold"),
            fg=ACCENT_GREEN,
            bg=BG_CARD,
        )
        c3_title.pack(anchor="w")

        # Bedtime Action Frame
        action_row = tk.Frame(card_sleep, bg=BG_CARD)
        action_row.pack(fill=tk.X, pady=(8, 10))

        self.btn_sleep = tk.Button(
            action_row,
            text="💤 I'M GOING TO SLEEP",
            font=("Segoe UI", 14, "bold"),
            bg=ACCENT_GREEN,
            fg=TEXT_WHITE,
            activebackground="#059669",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._toggle_sleep_session,
        )
        self.btn_sleep.pack(side=tk.LEFT)

        # Simulation mode checkbox for rapid demonstration
        self.simulation_mode_var = tk.BooleanVar(value=False)
        self.chk_sim = tk.Checkbutton(
            action_row,
            text="⚡ Simulation Mode (60x Speed for Demo / Testing)",
            variable=self.simulation_mode_var,
            font=("Segoe UI", 9),
            fg=TEXT_WHITE,
            bg=BG_CARD,
            selectcolor=BG_INPUT,
            activebackground=BG_CARD,
            activeforeground=TEXT_WHITE,
        )
        self.chk_sim.pack(side=tk.LEFT, padx=20)

        # Live Status Cards
        status_box = tk.Frame(card_sleep, bg=BG_INPUT, padx=12, pady=10)
        status_box.pack(fill=tk.X, pady=6)

        self.lbl_stage = tk.Label(
            status_box,
            text="Status: Standing by on your nightstand.",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE,
            bg=BG_INPUT,
            anchor="w",
        )
        self.lbl_stage.pack(fill=tk.X)

        self.lbl_countdown = tk.Label(
            status_box,
            text="Next REM Window: Not scheduled (Press 'I'm Going to Sleep' when in bed).",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_INPUT,
            anchor="w",
        )
        self.lbl_countdown.pack(fill=tk.X, pady=(2, 0))

        # Event Log Window
        tk.Label(
            card_sleep,
            text="Circadian Activity Log:",
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        ).pack(anchor="w", pady=(8, 2))

        self.log_text = scrolledtext.ScrolledText(
            card_sleep,
            height=5,
            font=("Consolas", 9),
            bg=BG_DARK,
            fg=TEXT_WHITE,
            relief=tk.FLAT,
            padx=8,
            pady=6,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self._log_event("Lucid Spork initialized. Wireless earbuds ready.")

    def _log_event(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)

    def _on_volume_changed(self, val):
        vol_pct = float(val)
        clamped_vol = vol_pct / 100.0
        self.player.set_volume(clamped_vol)
        self.vol_lbl.config(text=f"{int(vol_pct)}% (Whisper)")

    def _on_generate_clicked(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        api_key = self.api_key_var.get().strip()

        if not prompt:
            messagebox.showwarning("Prompt Missing", "Please enter what dream you want to experience.")
            return

        self.btn_generate.config(state=tk.DISABLED)
        self.gen_status_lbl.config(text="Connecting to Gemini API & drafting narrative...", fg=ACCENT_CYAN)

        def worker():
            try:
                self.dream_script_text = generate_dream_script(prompt, api_key=api_key)
                self.root.after(0, lambda: self.gen_status_lbl.config(text="Synthesizing audio narration..."))

                self.tts.synthesize(
                    self.dream_script_text,
                    output_path=self.generated_audio_path,
                )

                def on_done():
                    self.btn_generate.config(state=tk.NORMAL)
                    self.gen_status_lbl.config(text="Dream audio ready! Listen now.", fg=ACCENT_GREEN)
                    self._log_event("Dream audiobook synthesized successfully.")

                self.root.after(0, on_done)
            except Exception as e:
                def on_fail(err=e):
                    self.btn_generate.config(state=tk.NORMAL)
                    self.gen_status_lbl.config(text=f"Generation error: {err}", fg=ACCENT_RED)
                    self._log_event(f"Error during synthesis: {err}")
                self.root.after(0, on_fail)

        threading.Thread(target=worker, daemon=True).start()

    def _toggle_preview_audio(self):
        if self.player.is_playing():
            self.player.stop()
            self.btn_play_preview.config(text="🎧 Play Dream Audiobook Preview", bg=BG_INPUT)
            self._log_event("Preview audio stopped.")
        else:
            if not self.generated_audio_path.exists():
                messagebox.showinfo("Generate First", "Please click 'Generate Dream Audiobook' first to create your track.")
                return
            vol = float(self.vol_var.get()) / 100.0
            self.player.play(self.generated_audio_path, volume=vol)
            self.btn_play_preview.config(text="⏹️ Stop Preview", bg=ACCENT_VIOLET)
            self._log_event("Playing dream audiobook preview through earbuds.")

    def _play_calibration_test(self):
        sample = self.tts.ensure_calibration_sample()
        vol = float(self.vol_var.get()) / 100.0
        self.player.play(sample, volume=vol)
        self._log_event(f"Testing earbuds calibration tone at {int(vol * 100)}% whisper volume.")

    def _toggle_sleep_session(self):
        if self.is_session_active:
            # Cancel session
            if self.scheduler:
                self.scheduler.stop_session()
            self.is_session_active = False
            self.btn_sleep.config(text="💤 I'M GOING TO SLEEP", bg=ACCENT_GREEN)
            self.lbl_stage.config(text="Status: Sleep session halted.")
            self.lbl_countdown.config(text="Next REM Window: None.")
            self._log_event("Sleep session cancelled by user.")
        else:
            # Start session
            if not self.generated_audio_path.exists():
                # Auto-generate a default dream if user immediately hits sleep
                prompt = self.prompt_entry.get("1.0", tk.END).strip()
                self.dream_script_text = generate_dream_script(prompt, api_key=self.api_key_var.get().strip())
                self.tts.synthesize(self.dream_script_text, output_path=self.generated_audio_path)

            multiplier = 60.0 if self.simulation_mode_var.get() else 1.0
            whisper_vol = float(self.vol_var.get()) / 100.0

            self.scheduler = REMScheduler(
                audio_player=self.player,
                audio_path=self.generated_audio_path,
                whisper_volume=whisper_vol,
                time_multiplier=multiplier,
            )

            self.scheduler.on_tick = self._on_scheduler_tick
            self.scheduler.on_event = lambda msg: self.root.after(0, lambda: self._log_event(msg))

            self.scheduler.start_sleep_session()
            self.is_session_active = True
            self.btn_sleep.config(text="🛑 WAKE UP / CANCEL SESSION", bg=ACCENT_RED)

            mode_str = "SIMULATION (60x Speed)" if multiplier > 1.0 else "REAL-TIME CIRCADIAN"
            self._log_event(f"'I'm Going to Sleep' activated in {mode_str} mode. Sleep well!")

    def _on_scheduler_tick(self, status: dict):
        def update():
            rem_sec = status["seconds_until_next"]
            mins, secs = divmod(int(rem_sec), 60)
            hrs, mins = divmod(mins, 60)
            time_str = f"{hrs:02d}h {mins:02d}m {secs:02d}s"

            self.lbl_stage.config(text=f"Current State: {status['current_stage']}")
            self.lbl_countdown.config(
                text=f"Next Target: Cycle {status['next_cycle']} Peak REM ({status['next_target_time']}) — Infiltration in {time_str}"
            )
        self.root.after(0, update)
