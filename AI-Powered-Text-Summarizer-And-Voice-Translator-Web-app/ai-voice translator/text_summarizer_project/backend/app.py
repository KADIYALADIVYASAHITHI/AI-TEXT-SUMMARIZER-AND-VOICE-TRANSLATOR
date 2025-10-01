import os
import io
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import pipeline
import fitz  # PyMuPDF
import docx
from gtts import gTTS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from deep_translator import GoogleTranslator

# -----------------------
# Flask app
# -----------------------
app = Flask(__name__)
CORS(app)  # allow calls from the HTML file opened in the browser

# -----------------------
# Models (lazy/simple)
# -----------------------
# Summarizer (BART is a solid default)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Translation: load per target language on-demand to save RAM.
# (Helsinki-NLP MarianMT models are lightweight and reliable.)
TRANSLATION_MODELS = {
    "fr": "Helsinki-NLP/opus-mt-en-fr",
    "es": "Helsinki-NLP/opus-mt-en-es",
    "de": "Helsinki-NLP/opus-mt-en-de",
    "hi": "Helsinki-NLP/opus-mt-en-hi",
}
_loaded_translators = {}  # cache of pipelines

def get_translator(lang_code: str):
    if lang_code not in TRANSLATION_MODELS:
        raise ValueError("Unsupported language code.")
    if lang_code not in _loaded_translators:
        _loaded_translators[lang_code] = pipeline(
            "translation", model=TRANSLATION_MODELS[lang_code]
        )
    return _loaded_translators[lang_code]

# -----------------------
# Helpers
# -----------------------
def chunk_text(text, max_tokens=900):
    """
    Split very long text into manageable chunks for the summarizer.
    """
    parts = []
    current = []
    count = 0
    for para in text.split("\n"):
        tokens = para.strip().split()
        if not tokens:
            continue
        if count + len(tokens) > max_tokens and current:
            parts.append(" ".join(current))
            current, count = [], 0
        current.extend(tokens)
        count += len(tokens)
    if current:
        parts.append(" ".join(current))
    return parts if parts else [""]

def summarize_core(text: str, mode: str = "normal") -> str:
    """
    mode: 'normal' | 'detailed' | 'bullets'
    """
    text = (text or "").strip()
    if not text:
        return "No text provided."

    # summarize chunk-by-chunk then combine
    chunks = chunk_text(text)
    outputs = []
    for ch in chunks:
        if mode == "detailed":
            max_len, min_len = 220, 80
        else:
            max_len, min_len = 160, 50
        out = summarizer(
            ch, max_length=max_len, min_length=min_len, do_sample=False
        )[0]["summary_text"]
        outputs.append(out)

    summary = " ".join(outputs).strip()

    if mode == "bullets":
        # light bullet conversion: split into short sentences
        sentences = [s.strip() for s in summary.replace("\n", " ").split(".") if s.strip()]
        # keep up to 7 concise points
        bullets = sentences[:7]
        summary = "\n".join([f"• {b}." for b in bullets])

    return summary

def extract_text_from_filestorage(file_storage) -> str:
    filename = file_storage.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "txt":
        return file_storage.read().decode("utf-8", errors="ignore")

    if ext == "pdf":
        data = file_storage.read()
        doc = fitz.open(stream=data, filetype="pdf")
        text = []
        for page in doc:
            text.append(page.get_text())
        return "\n".join(text)

    if ext == "docx":
        doc = docx.Document(file_storage)
        text = []
        for p in doc.paragraphs:
            if p.text.strip():
                text.append(p.text)
        return "\n".join(text)

    raise ValueError("Unsupported file type. Use .txt, .pdf, or .docx")

def build_pdf_bytes(title: str, body: str) -> bytes:
    """
    Return a PDF as bytes: Title + body (wrapped across pages).
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, title)
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Body
    c.setFont("Helvetica", 12)
    y = height - 100
    # wrap body roughly by characters (simple but effective)
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            y -= 16
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50
            continue
        # ~95 chars per line at 12pt
        for i in range(0, len(line), 95):
            c.drawString(40, y, line[i:i+95])
            y -= 16
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50

    c.save()
    buf.seek(0)
    return buf.read()

# -----------------------
# API routes
# -----------------------
@app.route("/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    mode = data.get("mode", "normal")
    summary = summarize_core(text, mode)
    return jsonify({"summary": summary})

@app.route("/summarize_file", methods=["POST"])
def api_summarize_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    mode = request.form.get("mode", "normal")
    try:
        text = extract_text_from_filestorage(request.files["file"])
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    summary = summarize_core(text, mode)
    return jsonify({"summary": summary})

@app.route("/translate", methods=["POST"])
def api_translate():
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = data.get("text", "").strip()
        lang = data.get("lang", "en")

        if not text:
            return jsonify({"error": "No text provided."}), 400

        translated = GoogleTranslator(source="auto", target=lang).translate(text)

        return jsonify({
            "translated_text": translated,
            "lang": lang
        })

    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500
@app.route("/tts", methods=["POST"])
def api_tts():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    lang = data.get("lang", "en")  # gTTS supports many codes; use 'en' if unsure
    if not text:
        return jsonify({"error": "No text provided."}), 400

    # Save to a unique temp file
    fname = f"tts_{uuid.uuid4().hex}.mp3"
    path = os.path.join(os.getcwd(), fname)
    tts = gTTS(text=text, lang=lang)
    tts.save(path)

    # Return the file as a download stream (frontend can create an object URL)
    return send_file(path, as_attachment=True, download_name="summary_audio.mp3")

@app.route("/download_pdf", methods=["POST"])
def api_download_pdf():
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title", "AI Reader Summary")
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400
    pdf_bytes = build_pdf_bytes(title, text)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="summary.pdf",
    )

# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    # Access at http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=5000, debug=True)