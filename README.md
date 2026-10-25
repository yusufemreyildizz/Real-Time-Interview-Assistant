# Live Interview Panel 🎙️

A real-time, ultra-low latency interview assistant designed specifically for User Acquisition (UA) and Growth Marketing roles. 

This local web application captures live tab or microphone audio, processes it through Google's Gemini Live API, and streams back strategic, context-aware responses in real-time. It features a custom turn-detection algorithm to isolate questions and a distraction-free brutalist UI.

## ✨ Core Features

* **Zero-Latency Streaming:** Utilizes WebSockets and `asyncio` for non-blocking, real-time data transmission between the Vanilla JS frontend and FastAPI backend.
* **Smart Turn Detection:** Custom debounce logic (0.7s for questions, 1.3s for statements) accurately determines when the interviewer has finished speaking before generating strategic options.
* **Backchannel Filtering:** Automatically ignores conversational filler words (e.g., "mhm", "great", "okay") to prevent unnecessary API calls and UI updates.
* **Instant Translation & Categorization:** Streams real-time Turkish translations of English audio and automatically tags the question type (e.g., Technical UA, ROAS/Metrics, SKAN/Attribution, Culture Fit).
* **Brutalist UI:** A high-contrast, monochrome interface built with Tailwind CSS and JetBrains Mono, designed for split-second readability during live interviews without DOM layout thrashing.

## 🛠 Tech Stack

* **Backend:** Python, FastAPI, Uvicorn (uvloop), WebSockets
* **Frontend:** Vanilla JavaScript, HTML5, Web Audio API (AudioWorklet), Tailwind CSS
* **AI/LLM:** Google GenAI SDK (Gemini 2.0 Flash Live for real-time transcription, Gemini 2.5 Flash Lite for ultra-fast generation)

## 🚀 Installation & Setup

This project is designed to run locally on macOS.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/KULLANICI_ADIN/interview-panel-v2.git](https://github.com/KULLANICI_ADIN/interview-panel-v2.git)
   cd interview-panel-v2
