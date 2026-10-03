# AI Chatbot (Web UI)

## What I built
A single-page chatbot with a ChatGPT-style interface. You type a message in the browser, a small Python server sends it to Google's `gemini-2.5-flash` model, and the answer is streamed back and displayed on the page as it is written. The conversation is saved to a JSON file and reloaded automatically whenever the page is opened, so the chat continues where you left off.

This started as a command-line chatbot and was then converted into a web app with an HTML/CSS/JavaScript front end.

**Features**
- Clean, ChatGPT-style chat interface (dark theme, centered conversation, message composer at the bottom)
- Streaming responses with a typing indicator
- Conversation history saved to `chat_history.json` and loaded when the page opens
- System prompt to set the bot's behaviour
- "New chat" button to clear the saved conversation
- Basic Markdown rendering (code blocks, inline code, bold)
- Error handling: problems such as an invalid API key or rate limit are shown in the chat
- Enter to send, Shift+Enter for a new line

## Technology used
- **Python 3.9+**: backend language
- **Flask**: serves the page and exposes the chat API
- **Google Gemini API (`gemini-2.5-flash`)**: the AI model that generates the responses
- **OpenAI Python SDK (`openai`)**: used as the HTTP client, connected to Gemini's OpenAI-compatible endpoint
- **python-dotenv**: loads the API key, endpoint, and model name from a `.env` file
- **HTML, CSS, JavaScript**: the front end (no frameworks)
- **JSON**: stores the conversation history
- **Git & GitHub**: version control and hosting

## Project structure
```
.
├── app.py              # Flask backend: serves the page, calls Gemini, stores history
├── requirements.txt    # Python dependencies
├── .env.example        # Template for your environment variables
├── .gitignore
└── static/
    ├── index.html      # Page structure
    ├── style.css       # Styling
    └── script.js       # Chat logic: loads history, sends messages, shows streamed replies
```

## How to run

```bash
# 1. Clone the repo and enter the folder
git clone https://github.com/mirfan723/ai-chatbot.git
cd ai-chatbot

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux

# 5. Start the server
python app.py
```

Then open **http://localhost:5000** in your browser.

### Environment variables
Get a free API key from [Google AI Studio](https://aistudio.google.com) and add it to `.env`:

```
OPENAI_API_KEY=your-gemini-api-key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
MODEL=gemini-2.5-flash
```

The variable is called `OPENAI_API_KEY` because the OpenAI library looks for that name, but the value is your **Gemini** key.

## API integration approach
1. **Browser to server:** `script.js` sends the user's message to the Flask backend with `POST /api/chat`. The browser never talks to Gemini directly, so the API key stays on the server and is never exposed.
2. **Server to Gemini:** the backend uses the OpenAI Python library pointed at Gemini's OpenAI-compatible endpoint. The endpoint, key, and model name come from `.env`, so switching AI providers needs a config change and no code change.
3. **Memory:** the conversation is kept as a list of messages: `{"role": "system" | "user" | "assistant", "content": "..."}`. The API is stateless, so on every request the **whole list** is sent to `client.chat.completions.create(model=MODEL, messages=..., stream=True)`. That is what gives the bot its memory.
4. **Streaming:** the server forwards the reply chunk by chunk, and the page reads the stream and updates the message as text arrives.
5. **Persistence:** after each completed reply, the conversation is written to `chat_history.json`.
6. **Loading history:** when the page opens, `script.js` calls `GET /api/history` and renders the saved messages.
7. **Errors:** if the API call fails, the failed message is not saved to the history, and a readable error is displayed in the chat.

### API endpoints
| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Serves the chat page |
| GET | `/api/history` | Returns the saved conversation |
| POST | `/api/chat` | Sends a message and streams back the reply |
| POST | `/api/clear` | Clears the saved conversation |

## What I learned
- Chat APIs are stateless: the bot's memory is just resending previous messages with every request.
- API keys must stay on the server. A web page can't call the AI provider directly without exposing the key, so a small backend is needed.
- Many AI providers share the OpenAI-compatible format, which makes switching between them easy.
- How streaming works end to end, from the model to the server to the browser.
- How to structure a simple full-stack project: a Python API with a plain HTML/CSS/JS front end.
- Never commit secrets: use `.env` files and `.gitignore`.

## What I would improve next
- Support multiple saved conversations with a sidebar, like ChatGPT
- Render full Markdown (lists, headings, tables) with a library
- Trim or summarise old messages to stay within the model's context window
- Add a stop-generating button and a copy button on replies
- Add a light theme and a theme toggle
- Add user accounts so each person has their own history
- Add voice input and voice output
- Deploy the app online

## Screenshot
<img width="1911" height="902" alt="image" src="https://github.com/user-attachments/assets/1e0f13da-8186-48a4-bf25-bf467ed93b28" />
