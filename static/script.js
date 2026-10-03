const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const clearBtn = document.getElementById("clear");
const empty = document.getElementById("empty");

let busy = false;

// Escape HTML, then apply minimal markdown (code blocks, inline code, bold)
function render(text) {
  const safe = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return safe
    .replace(/```(?:\w+)?\n?([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
    .replace(/`([^`\n]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
}

function addMessage(role, text) {
  empty.style.display = "none";
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "user") bubble.textContent = text;
  else bubble.innerHTML = render(text);
  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const messages = await res.json();
    messages.forEach((m) => addMessage(m.role === "user" ? "user" : "bot", m.content));
  } catch {
    addMessage("bot", "Could not load history. Is the server running?").classList.add("error");
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || busy) return;

  busy = true;
  sendBtn.disabled = true;
  input.value = "";
  input.style.height = "auto";
  addMessage("user", text);

  const bubble = addMessage("bot", "");
  bubble.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';

  let reply = "";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    if (!res.ok) throw new Error((await res.json()).error || "Request failed.");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      reply += decoder.decode(value, { stream: true });
      const errAt = reply.indexOf("\x00");
      if (errAt !== -1) throw new Error(reply.slice(errAt + 1));
      bubble.innerHTML = render(reply);
      chat.scrollTop = chat.scrollHeight;
    }
  } catch (err) {
    bubble.classList.add("error");
    bubble.textContent = `Something went wrong: ${err.message}`;
  }

  busy = false;
  sendBtn.disabled = false;
  input.focus();
}

clearBtn.addEventListener("click", async () => {
  if (busy) return;
  await fetch("/api/clear", { method: "POST" });
  chat.querySelectorAll(".msg").forEach((el) => el.remove());
  empty.style.display = "";
});

sendBtn.addEventListener("click", send);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = input.scrollHeight + "px";
});

loadHistory();
