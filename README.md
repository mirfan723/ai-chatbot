# Basic AI Chatbot (CLI)

## What I built
A command-line chatbot in Python. You type a message, it is sent to OpenAI's `gpt-4o-mini` model, and the answer is streamed back into the terminal. The full conversation is saved to a JSON file, so the bot remembers earlier messages even after you restart the program.

**Features**
- End-to-end chat: input → API → response → display
- Conversation history (sent with every request, saved to `chat_history.json`)
- System prompt to set the bot's behaviour
- Streaming responses with a "Thinking..." loading state
- Error handling (missing/invalid API key, rate limit, no internet, API errors)
- Chat commands: `/history`, `/clear`, `/exit`


## How to run

```bash
# 1. Clone the repo and enter the folder
git clone <your-repo-url>
cd ai-chatbot

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env            # then edit .env and paste your key
# or: export OPENAI_API_KEY="sk-..."

# 5. Start chatting
python chatbot.py
```

## API integration approach
1. The conversation is kept as a list of messages: `{"role": "system" | "user" | "assistant", "content": "..."}`.
2. On every turn, the new user message is appended to the list and the **whole list** is sent to `client.chat.completions.create(model="gpt-4o-mini", messages=..., stream=True)`. The API is stateless, so sending the full history is what gives the bot its memory.
3. The reply is streamed chunk by chunk and printed as it arrives, then appended to the list as an `assistant` message.
4. After each turn the list is written to `chat_history.json`; on startup it is loaded again.
5. If an API call fails, the failed user message is removed from the history so the conversation stays clean, and a readable error is shown.

## What I learned
- Chat APIs are stateless: memory is just resending previous messages.
- How roles (system / user / assistant) shape the model's behaviour.
- Streaming makes the bot feel much faster than waiting for the full answer.
- Handling API errors separately (auth, rate limits, network) gives much better user feedback.
- Never hard-code API keys; use environment variables and `.gitignore`.

## Screenshot / demo
_Add a screenshot or a short screen recording of the chatbot running here._
