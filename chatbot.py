#!/usr/bin/env python3
"""
Basic AI Chatbot (CLI)
----------------------
- Takes user input from the terminal
- Sends it (plus full conversation history) to gemini-2.5-flash
- Streams the reply back to the terminal
- Saves conversation history to a JSON file so it persists between runs
"""

import json
import os
import sys
from pathlib import Path

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

try:
    from dotenv import load_dotenv

    load_dotenv()  # reads the gemini-2.5-flash API key and settings from a .env file if present
except ImportError:
    pass  

MODEL = os.getenv("MODEL")
HISTORY_FILE = Path("chat_history.json")
SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Keep answers clear and concise unless the user asks for more detail."
)

# Simple ANSI colors 
BLUE, GREEN, GRAY, RED, RESET = "\033[94m", "\033[92m", "\033[90m", "\033[91m", "\033[0m"


# ---------- History handling ----------
def load_history() -> list[dict]:
    """Load saved messages from disk, or start fresh with the system prompt."""
    if HISTORY_FILE.exists():
        try:
            messages = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if isinstance(messages, list) and messages:
                messages[0] = {"role": "system", "content": SYSTEM_PROMPT}
                return messages
        except (json.JSONDecodeError, OSError):
            print(f"{GRAY}Could not read history file, starting fresh.{RESET}")
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_history(messages: list[dict]) -> None:
    try:
        HISTORY_FILE.write_text(
            json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as e:
        print(f"{RED}Warning: could not save history: {e}{RESET}")


def show_history(messages: list[dict]) -> None:
    turns = [m for m in messages if m["role"] != "system"]
    if not turns:
        print(f"{GRAY}(no conversation history yet){RESET}")
        return
    for m in turns:
        who, color = ("You", BLUE) if m["role"] == "user" else ("Bot", GREEN)
        print(f"{color}{who}:{RESET} {m['content']}\n")


# ---------- Talking to the API ----------
def get_reply(client: OpenAI, messages: list[dict]) -> str:
    """Send the conversation to the model and stream the answer to the terminal."""
    print(f"{GRAY}Thinking...{RESET}", end="\r", flush=True)  # loading state

    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
    )

    reply_parts: list[str] = []
    first_chunk = True
    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if not delta:
            continue
        if first_chunk:
            print(" " * 20, end="\r")  
            print(f"{GREEN}Bot:{RESET} ", end="", flush=True)
            first_chunk = False
        print(delta, end="", flush=True)
        reply_parts.append(delta)

    print("\n")
    return "".join(reply_parts)


def main() -> None:
    api_key = os.getenv("Gemini_API_KEY")
    if not api_key:
        print(
            f"{RED}Gemini_API_KEY is not set.{RESET}\n"
            "Set it in your terminal or in a .env file, e.g.\n"
            "  export OPENAI_API_KEY='sk-...'      (macOS/Linux)\n"
            "  setx OPENAI_API_KEY \"sk-...\"        (Windows)"
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    messages = load_history()

    previous = len(messages) - 1
    print(f"{GREEN}=== AI Chatbot ({MODEL}) ==={RESET}")
    print(f"{GRAY}Commands: /history  /clear  /exit{RESET}")
    if previous > 0:
        print(f"{GRAY}Loaded {previous} previous messages from {HISTORY_FILE}.{RESET}")
    print()

    while True:
        try:
            user_input = input(f"{BLUE}You:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Commands
        cmd = user_input.lower()
        if cmd in ("/exit", "/quit"):
            print("Goodbye!")
            break
        if cmd == "/history":
            show_history(messages)
            continue
        if cmd == "/clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            save_history(messages)
            print(f"{GRAY}History cleared.{RESET}\n")
            continue

        # Normal chat turn
        messages.append({"role": "user", "content": user_input})
        try:
            reply = get_reply(client, messages)
        except AuthenticationError:
            print(f"{RED}Invalid API key. Check OPENAI_API_KEY.{RESET}")
            messages.pop()
            continue
        except RateLimitError:
            print(f"{RED}Rate limit or quota exceeded. Check your Gemini API quota/usage.{RESET}")
            messages.pop()
            continue
        except APIConnectionError:
            print(f"{RED}Could not connect to Gemini. Check your internet connection.{RESET}")
            messages.pop()
            continue
        except APIStatusError as e:
            print(f"{RED}API error ({e.status_code}): {e.message}{RESET}")
            messages.pop()
            continue
        except KeyboardInterrupt:
            print(f"\n{GRAY}(response interrupted){RESET}\n")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": reply})
        save_history(messages)


if __name__ == "__main__":
    main()