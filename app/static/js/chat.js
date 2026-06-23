(() => {
  const form = document.getElementById("message-form");
  const input = document.getElementById("message-input");
  const messages = document.getElementById("messages");
  const connectionStatus = document.getElementById("connection-status");
  const currentUserId = window.CHAT_CURRENT_USER_ID;

  if (!form || !input || !messages || typeof io === "undefined") return;

  const socket = io({ transports: ["websocket", "polling"] });

  const setStatus = (label, state) => {
    connectionStatus.textContent = label;
    connectionStatus.className = `connection-status ${state ? `is-${state}` : ""}`;
    const dot = document.createElement("span");
    dot.className = "status-dot";
    connectionStatus.prepend(dot);
  };

  const escapeHTML = (value) => {
    const el = document.createElement("div");
    el.textContent = value;
    return el.innerHTML;
  };

  const scrollToBottom = () => { messages.scrollTop = messages.scrollHeight; };

  const renderMessage = (message) => {
    document.getElementById("empty-state")?.remove();
    const own = Number(message.author_id) === Number(currentUserId);
    const article = document.createElement("article");
    article.className = `message${own ? " message--own" : ""}`;
    article.id = `message-${message.id}`;
    let deleteButtonHTML = "";
    if (own) {
      deleteButtonHTML = `
        <button class="button button--icon-only button--danger" data-delete-message-id="${message.id}" aria-label="Borrar mensaje">
          <span aria-hidden="true">🗑️</span>
        </button>`;
    }
    article.innerHTML = `
      <div class="message-meta">
        <strong>${own ? "Tú" : escapeHTML(message.author_name)}</strong>
        <time>${escapeHTML(message.created_at)}</time>
        ${deleteButtonHTML}
      </div>
      <p>${escapeHTML(message.body)}</p>`;
    messages.append(article);
    scrollToBottom();
  };

  const deleteMessage = async (messageId) => {
    try {
      const response = await fetch(`/delete_message/${messageId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || "Error al borrar el mensaje.");
      }
    } catch (error) {
      console.error("Error deleting message:", error);
      window.alert(error.message);
    }
  };

  socket.on("connect", () => setStatus("Conectado", "online"));
  socket.on("disconnect", () => setStatus("Sin conexión", "offline"));
  socket.on("connect_error", () => setStatus("No se pudo conectar", "offline"));
  socket.on("new_message", renderMessage);
  socket.on("message_deleted", ({ message_id }) => {
    const messageElement = document.getElementById(`message-${message_id}`);
    if (messageElement) {
      messageElement.remove();
    }
  });
  socket.on("message_error", ({ message }) => window.alert(message));

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const body = input.value.trim();
    if (!body || !socket.connected) return;
    socket.emit("send_message", { body });
    input.value = "";
    input.style.height = "auto";
    input.focus();
  });

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 130)}px`;
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  messages.addEventListener("click", (event) => {
    const deleteButton = event.target.closest("[data-delete-message-id]");
    if (!deleteButton) return;

    const messageId = deleteButton.dataset.deleteMessageId;
    if (!messageId) return;

    if (window.confirm("¿Estás seguro de que quieres borrar este mensaje?")) {
      deleteMessage(messageId);
    }
  });

  scrollToBottom();
})();