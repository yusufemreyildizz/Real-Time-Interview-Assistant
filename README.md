# Real-Time Interview Assistant 🎙️

A low-latency, real-time conversation assistant that adapts to any profession, industry, or scenario.

This local web app captures live tab or microphone audio, streams it through Google's Gemini Live API, and returns a live transcript, a translation, and context-aware reply suggestions. Paste your background, a job description, or any brief into the **System Context** field, and the assistant tailors its suggestions to your exact situation. It works for job interviews, client calls, sales meetings, language practice, and more.

## ✨ Core Features

* **Dynamic Contextualization:** The "System Context" field accepts a CV summary, job description, or free-form brief. Change it at any time to switch roles, industries, or scenarios.
* **Live Translation:** Shows the original speech and its translation side by side. Translation is handled by Gemini, so it is not limited to a single language pair.
* **Low-Latency Streaming:** WebSockets and `asyncio` provide non-blocking, real-time data flow between the vanilla JS frontend and the FastAPI backend.
* **Smart Turn Detection:** Custom debounce logic (0.7s after questions, 1.3s after statements) detects when the speaker has finished before generating suggestions.
* **Backchannel Filtering:** Ignores filler responses ("mhm", "great", "okay") to avoid unnecessary API calls and UI updates.
* **Quick Reply Suggestions:** Generates three context-aware reply options per turn, copyable with one click.
* **Brutalist UI:** A high-contrast, monochrome interface built with Tailwind CSS and JetBrains Mono, designed for split-second readability.

## 🛠 Tech Stack

* **Backend:** Python, FastAPI, Uvicorn (uvloop), WebSockets
* **Frontend:** Vanilla JavaScript, HTML5, Web Audio API (AudioWorklet), Tailwind CSS (CDN)
* **AI:** Google GenAI SDK. The Gemini Live API handles real-time audio transcription, and a fast Gemini Flash-Lite model handles translation and suggestion generation.

## 🚀 Installation & Setup

Designed to run locally. Tested on macOS with Google Chrome.

**1. Clone the repository**

```bash
git clone https://github.com/yusufemreyildizz/Real-Time-Interview-Assistant.git
cd Real-Time-Interview-Assistant
```

**2. Create a virtual environment and install dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Add your API key**

Get a key from [Google AI Studio](https://aistudio.google.com/), then create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

> Never commit your `.env` file. It is already listed in `.gitignore`.

## 💻 Usage

Start the server:

```bash
uvicorn main:app --port 8002
```

Open `http://localhost:8002` in Google Chrome, then:

1. Describe your scenario in the **System Context** field (role, industry, job description, or any brief). This is optional but improves suggestion quality.
2. Choose an audio source:
   * **Sekme Sesi (Tab Audio):** captures audio from a Google Meet, Zoom, or Teams browser tab. When Chrome asks what to share, select the tab and check **"Share tab audio"**.
   * **Mikrofon (Microphone):** captures your own microphone, useful for testing.
3. Click **Dinle (Listen)**. The transcript, translation, and three reply options appear in real time.
4. Click any reply card to copy it to your clipboard.
5. You can also type a sentence manually and press Enter.

## 🔒 Privacy & Responsible Use

* Audio is streamed to Google's Gemini API for processing. Review Google's API terms and privacy policy before using it with sensitive conversations.
* Keep your API key private. Rotate it immediately if it is ever exposed.
* Check the rules of your interview, employer, or platform, and the recording laws where you live, before using any real-time assistant in a live conversation. Get consent from other participants where required.

## 📄 License

Add a license of your choice (e.g. MIT) as a `LICENSE` file.
