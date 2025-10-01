# AI Reader — Text Summarizer + Translator + TTS (HTML/CSS Frontend + Flask Backend)

## Features
- Summarize text or files (.txt, .pdf, .docx)
- Modes: Normal / Detailed / Bullet Points
- Translate summary (en → fr/es/de/hi)
- Text‑to‑Speech (pick language; uses gTTS)
- Download summary as PDF

## Setup

### 1) Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
