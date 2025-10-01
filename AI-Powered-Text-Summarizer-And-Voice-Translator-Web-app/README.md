# 📘 AI-Powered Text Summarizer, Translator & Speech Generator

## 🔹 Project Overview

This project is an **AI-powered web application** that allows users to:

1. **Summarize** long text into concise key points.
2. **Translate** the text into multiple Indian and global languages.
3. **Convert text into speech (TTS)** for accessibility and inclusivity.

It is built using **Flask (Python backend)**, **BART model (summarization)**, **Deep Translator (translation)**, and **gTTS (speech synthesis)**. The frontend is built with **HTML, CSS, and JavaScript**.

---

## 🔹 Problem Statement & Motivation

* Reading long documents is **time-consuming**.
* **Language barriers** limit access to knowledge in India’s multilingual society.
* **Visually impaired individuals** struggle to read text.

✅ Our solution: An all-in-one system that **summarizes, translates, and speaks** text for better accessibility, productivity, and inclusivity.

---

## 🔹 Features

* 📑 **Automatic Text Summarization** (powered by BART).
* 🌍 **Multi-language Translation** (English, Hindi, Tamil, Telugu, Kannada, etc.).
* 🔊 **Text-to-Speech Conversion** (clear, natural voice output).
* 📂 **Upload & Process Documents** (PDF, DOCX, TXT).
* 💾 **Export Results** as **PDF reports** or **MP3 audio**.
* 🎯 **User-Friendly UI** with real-time feedback messages.

---

## 🔹 Tech Stack

### **Frontend**

* HTML, CSS, JavaScript

### **Backend**

* Python (Flask Framework)
* REST API for communication

### **AI Models & Libraries**

* **BART (HuggingFace Transformers)** → Text Summarization
* **Deep Translator** → Multi-language Translation
* **gTTS (Google Text-to-Speech)** → Speech Generation

---

## 🔹 System Architecture

```
User → Frontend (HTML/JS) → REST API (Flask) → Models (BART, Translator, gTTS) → Response (Summary/Translation/Audio)
```

---

## 🔹 How It Works (Workflow)

1. User pastes text or uploads a file.
2. Clicks **Summarize** → Backend summarizes using BART.
3. Clicks **Translate** → Text translated to chosen language.
4. Clicks **Speak** → Text converted to audio (MP3).
5. User can download results (text/audio/PDF).

---

## 🔹 REST API Endpoints

* `POST /summarize` → Summarize text.
* `POST /translate` → Translate text.
* `POST /speak` → Convert text to speech.

Example request (JSON):

```json
{
  "text": "Artificial Intelligence is transforming healthcare.",
  "lang": "hi"
}
```

Example response (JSON):

```json
{
  "summary": "AI is transforming healthcare.",
  "translation": "कृत्रिम बुद्धिमत्ता स्वास्थ्य सेवा को बदल रही है।",
  "audio": "audio_file.mp3"
}
```

---

## 🔹 Societal Impact

* ⏳ Saves time for students, researchers, and professionals.
* 🌍 Breaks **language barriers** across Indian regional languages.
* ♿ Empowers **visually impaired users** with speech output.
* 📚 Increases accessibility to education and information.

---

## 🔹 Future Enhancements

* Add **OCR (Optical Character Recognition)** to process images & scanned documents.
* Support **more Indian & foreign languages**.
* Use **Neural TTS** for more natural speech.
* Mobile app version for wider accessibility.

---

---

## 🔹 Installation & Setup

### **1. Clone the Repository**

```bash
git clone https://github.com/yourusername/ai-text-summarizer-translator.git
cd ai-text-summarizer-translator
```

### **2. Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run Flask Server**

```bash
python app.py
```

### **5. Open in Browser**

```
http://127.0.0.1:5000
```

---

## 🔹 Demo Screenshot

(Add your project screenshot here)

---

## 🔹 License

📜 Open-source project for educational purposes.
