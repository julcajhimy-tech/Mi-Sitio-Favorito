(() => {
  // --- Selección de elementos del DOM ---
  const form = document.getElementById("message-form");
  const input = document.getElementById("message-input");
  const messages = document.getElementById("messages");
  const connectionStatus = document.getElementById("connection-status");
  const attachButton = document.getElementById("attach-button");
  const mediaInput = document.getElementById("media-input");
  const muteButton = document.getElementById("mute-button");
  const currentUserId = window.CHAT_CURRENT_USER_ID;
  const notificationSound = new Audio("/static/sounds/notification.mp3");
  let isMuted = false;

  if (!form || !input || !messages || !attachButton || !mediaInput || !muteButton || typeof io === "undefined") {
    console.error("Elementos del chat no encontrados. Saliendo.");
    return;
  }

  // --- Conexión con Socket.IO ---
  const socket = io({ transports: ["websocket", "polling"] });

  // --- Funciones auxiliares ---
  const setStatus = (label, state) => {
    connectionStatus.textContent = label;
    connectionStatus.className = `connection-status ${state ? `is-${state}` : ""}`;
    const dot = document.createElement("span");
    dot.className = "status-dot";
    connectionStatus.prepend(dot);
  };

  const toggleMute = () => {
    isMuted = !isMuted;
    muteButton.querySelector("span").textContent = isMuted ? "🔇" : "🔊";
    muteButton.setAttribute("aria-label", isMuted ? "Activar notificaciones" : "Silenciar notificaciones");
  };

  const escapeHTML = (value) => {
    const el = document.createElement("div");
    el.textContent = value;
    return el.innerHTML;
  };

  const scrollToBottom = () => { messages.scrollTop = messages.scrollHeight; };

  const getMessageBodyHTML = (message) => {
    switch (message.message_type) {
      case "image":
        return `
          <a href="${message.media_url}" target="_blank" rel="noopener noreferrer">
            <img src="${message.media_url}" alt="Imagen adjunta" class="message-image">
          </a>`;
      case "audio":
        return `<audio controls src="${message.media_url}" class="message-audio"></audio>`;
      case "document":
        return `
          <a href="${message.media_url}" target="_blank" rel="noopener noreferrer" class="message-document">
            📄 ${escapeHTML(message.body)}
          </a>`;
      default:
        return `<p>${escapeHTML(message.body)}</p>`;
    }
  };

  // --- Renderizado de mensajes ---
  const renderMessage = (message) => {
    document.getElementById("empty-state")?.remove();
    const own = Number(message.author_id) === Number(currentUserId);
    const article = document.createElement("article");
    article.className = `message${own ? " message--own" : ""}`;
    article.id = `message-${message.id}`;
    
    const deleteButtonHTML = own ? `
      <button class="button button--icon-only button--danger" data-delete-message-id="${message.id}" aria-label="Borrar mensaje">
        <span aria-hidden="true">🗑️</span>
      </button>` : "";

    article.innerHTML = `
      <div class="message-meta">
        <strong>${own ? "Tú" : escapeHTML(message.author_name)}</strong>
        <time>${new Date(message.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}</time>
        ${deleteButtonHTML}
      </div>
      <div class="message-body">${getMessageBodyHTML(message)}</div>`;
      
    messages.append(article);

    if (!own && !isMuted) {
      notificationSound.play().catch(error => {
        // La reproducción automática puede fallar si el usuario no ha interactuado con la página.
        console.warn("No se pudo reproducir el sonido de notificación:", error);
      });
    }

    scrollToBottom();
  };

  // --- Acciones de la API ---
  const deleteMessage = async (messageId) => {
    try {
      const response = await fetch(`/delete_message/${messageId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || "Error al borrar el mensaje.");
      }
    } catch (error) {
      console.error("Error deleting message:", error);
      window.alert(error.message);
    }
  };

  const uploadMedia = async (file) => {
    console.log(`Iniciando subida para el archivo: ${file.name}`); // Log para depuración
    const formData = new FormData();
    formData.append("media_file", file);

    try {
      const response = await fetch("/upload_media", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const text = await response.text();
        if (text.trim().startsWith("<!doctype html")) {
          window.location.reload();
          return;
        }
        const result = JSON.parse(text);
        throw new Error(result.error || "Error al subir el archivo.");
      }
    } catch (error) {
      console.error("Error uploading media:", error);
      if (error.message.includes("reload")) return;
      window.alert(error.message);
    } finally {
      console.log("Finalizada la operación de subida."); // Log para depuración
    }
  };

  // --- Inicialización de manejadores de eventos ---
  const initializeEventListeners = () => {
    socket.on("connect", () => setStatus("Conectado", "online"));
    socket.on("disconnect", () => setStatus("Sin conexión", "offline"));
    socket.on("connect_error", () => setStatus("No se pudo conectar", "offline"));
    socket.on("new_message", renderMessage);
    socket.on("message_deleted", ({ message_id }) => {
      document.getElementById(`message-${message_id}`)?.remove();
    });
    socket.on("message_error", ({ message }) => window.alert(message));

    muteButton.addEventListener("click", toggleMute);

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const body = input.value.trim();
      if (!body || !socket.connected) return;
      socket.emit("send_message", { body });
      input.value = "";
      input.style.height = "auto";
      input.focus();
    });

    attachButton.addEventListener("click", () => {
      mediaInput.click();
    });

    mediaInput.addEventListener("change", () => {
      const file = mediaInput.files[0];
      if (file && socket.connected) {
        uploadMedia(file);
      }
      mediaInput.value = ""; // Reset para poder subir el mismo archivo de nuevo
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
      if (deleteButton && window.confirm("¿Estás seguro de que quieres borrar este mensaje?")) {
        deleteMessage(deleteButton.dataset.deleteMessageId);
      }
    });
  };

  // --- Punto de entrada ---
  initializeEventListeners();
  scrollToBottom();
})();