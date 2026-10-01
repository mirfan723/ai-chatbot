# Basic AI Chatbot (CLI)

## What I built
A command-line chatbot in Python. You type a message, it is sent to Google's `gemini-2.5-flash` model, and the answer is streamed back into the terminal. The full conversation is saved to a JSON file, so the bot remembers earlier messages even after you restart the program.

## Technology used
- **Python 3.9+**: main programming language
- **Google Gemini API (`gemini-2.5-flash`)**: the AI model that generates the responses
- **OpenAI Python SDK (`openai`)**: used as the HTTP client, connected to Gemini's OpenAI-compatible endpoint
- **python-dotenv**: loads the API key, endpoint, and model name from a `.env` file
- **JSON**: stores the conversation history in `chat_history.json`
- **Git & GitHub**: version control and hosting

## **Features**
- End-to-end chat: input → API → response → display
- Conversation history (sent with every request, saved to `chat_history.json`)
- System prompt to set the bot's behaviour
- Streaming responses with a "Thinking..." loading state
- Error handling (missing/invalid API key, rate limit, no internet, API errors)
- Chat commands: `/history`, `/clear`, `/exit`


## API integration approach
1. The conversation is kept as a list of messages: `{"role": "system" | "user" | "assistant", "content": "..."}`.
2. The chatbot uses the OpenAI Python library, pointed at Gemini's OpenAI-compatible endpoint (`https://generativelanguage.googleapis.com/v1beta/openai/`). The endpoint, API key, and model name (`gemini-2.5-flash`) are set in a `.env` file, so switching providers needs a config change and no code change.
3. On every turn, the new user message is appended to the list and the **whole list** is sent to `client.chat.completions.create(model=MODEL, messages=..., stream=True)`. The API is stateless, so sending the full history is what gives the bot its memory.
4. The reply is streamed chunk by chunk and printed as it arrives, then appended to the list as an `assistant` message.
5. After each turn the list is written to `chat_history.json`; on startup it is loaded again.
6. If an API call fails, the failed user message is removed from the history so the conversation stays clean, and a readable error is shown.

## Screenshot 
<img width="983" height="492" alt="Screenshot 2026-10-01 182602" src="https://github.com/user-attachments/assets/07ed0247-6d21-4b61-b5eb-f34d2954f31b" />

