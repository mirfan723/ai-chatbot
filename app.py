"""Web backend for the chatbot: serves the page and streams Gemini replies.
The API key stays on the server and is never exposed to the browser."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("MODEL")
HISTORY_FILE = Path("chat_history.json")
SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Keep answers clear and concise unless the user asks for more detail."
)

# Reads OPENAI_API_KEY and OPENAI_BASE_URL (Gemini endpoint) from .env
client = OpenAI(api_key=os.getenv("Gemini_API_KEY"))
app = Flask(__name__, static_folder="static", static_url_path="")


def load_history():
    try:
        messages = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(messages, list) and messages:
            messages[0] = {"role": "system", "content": SYSTEM_PROMPT}
            return messages
    except (OSError, json.JSONDecodeError):
        pass
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_history(messages):
    HISTORY_FILE.write_text(json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8")


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/history")
def history():
    return jsonify([m for m in load_history() if m["role"] != "system"])


@app.post("/api/clear")
def clear():
    save_history([{"role": "system", "content": SYSTEM_PROMPT}])
    return jsonify(ok=True)


@app.post("/api/chat")
def chat():
    text = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not text:
        return jsonify(error="Message is empty."), 400

    messages = load_history()
    messages.append({"role": "user", "content": text})

    def generate():
        parts = []
        try:
            stream = client.chat.completions.create(model=MODEL, messages=messages, stream=True)
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    parts.append(delta)
                    yield delta
        except Exception as e:  # \x00 prefix tells the page this is an error
            yield "\x00" + str(getattr(e, "message", e))
            return
        messages.append({"role": "assistant", "content": "".join(parts)})
        save_history(messages)

    return Response(generate(), mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
