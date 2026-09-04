# 🥄 Lucid Spork

> **Dream Control & Targeted Lucid Dream Incubation using Python, Gemini API, and Timing.IM ALSO ADDING MULTIPLAYER DREAMS SOON AND DREAM RECORDING**


---

## 🌌 What is Lucid Spork?

**Lucid Spork** is a super cool project ive been working on for months which can control your dreams with nothing but a PC and wireless earbuds, but im later to expand it.So it uses timing and detects rem sleep , but beforehand you enter what dream you want, then it turns it into a dream audio book using ana LLM and TTS (all for free with gemini api) then if you are in the dreaming state it plays the audio, which will then change your dreams

All you need is a computer running Python and a comfortable pair of **wireless earbuds**.

You describe whatever dream you want to go through , Lucid Spork feeds your prompt into **Google Gemini**, transforms it into a  audiobook-style narrative, converts it to speech using neural Text-to-Speech (TTS), and uses precise **REM sleep timing algorithms** to whisper the dream script directly into your ears during your deepest dream states.

---

## ⚡ How It Works

```
 ┌──────────────────────┐
 │  Input Dream Prompt  │  ("I want to fly through a land made of sporks...")
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │   Google Gemini API  │  Generates an immersive, second-person  script
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │  TTS Generator │  Synthesizes calming  audiobook audio
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Wakeful listening Mode │  Listen 2-3x while awake to get you used to it
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │  Volume Calibration  │  Fine-tune to whisper level (audible, but won't wake you)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │  "Going to Sleep"    │  Press button -> Enters circadian sleep delay
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │   REM Timing Queue   │  Injects narrative audio precisely inside REM dream windows
 └──────────────────────┘
```


---

## 🎧 Hardware Requirements

- **Wireless Earbuds**: Any standard Bluetooth earbuds or sleep headphones (flat headband-style sleep earphones are highly recommended for side sleepers).
- **Host Machine**: Any PC, laptop, or Raspberry Pi capable of running Python 3.10+.

---



---

## 🛠️ Usage Step-by-Step

### Step 1: Dream Input
Enter what you wish to experience:
```text
> Enter your dream prompt:
Explore a Land  made of sporks
```

### Step 2: Generation & Preview
Gemini produces the story script and exports `dream_audio.wav`. Listen to it once or twice in bed with your earbuds in to get u used to it.

### Step 3: Calibrate Volume
make it so it doesnt wake you up but it is not too quiet that you wont hear it
### Step 4: Bedtime Activation
When your eyes get heavy and you're ready to drift off, click:
```text
[ 💤 I'M GOING TO SLEEP ]https://github.com/notsilverspork-web/Lucid-Spork/blob/main/readme.md
```

---

---

## 🗺️ Upcoming Features


- [ 😭] **Multiplayer Dreams**: Just imagine u and ur bro dreaming together
- [🔥📷 ] **4K Dream Recording**: using advanced text to video models to turn ur dream into  a 4k video.
- [ ⌚] **Smart Wearable Integration**: Optional BLE hooks for Apple Watch / Whoop / Fitbit to trigger based on live heart-rate variability (HRV) rather than pure timing.

---

## ⚠️ Disclaimer & Safety

- **Hearing Safety**: Always calibrate audio volume to comfortable whisper levels before sleeping. Do not play audio at high volumes through headphones for extended periods.
- **Sleep Quality**: Lucid dreaming techniques should not replace healthy, restorative sleep. If you experience sleep disruption, discontinue use.

---

## 👤 Author & Credits

- **Founder **: **Notsilverspork (Niko)** 

Contributions, feature ideas, and sleep logs are welcome! 
