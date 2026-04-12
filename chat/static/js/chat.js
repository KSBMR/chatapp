/**
 * ════════════════════════════════════════════
 * Django Chat App — WebSocket Client
 * 
 * How it works:
 * 1. On page load, we open a WebSocket connection to the server.
 * 2. When the user types and hits Enter / clicks Send,
 *    we send a JSON message over the WebSocket.
 * 3. The server (ChatConsumer) receives it, saves it to DB,
 *    and broadcasts it to both users in the room.
 * 4. Our onmessage handler receives the broadcast and renders
 *    the new message bubble in the chat window.
 * ════════════════════════════════════════════
 */

(function () {
  "use strict";

  // ── Configuration from data attributes ────────────────────────────────────
  const chatApp = document.getElementById("chat-app");
  if (!chatApp) return; // Not on a chat page

  const currentUser    = chatApp.dataset.currentUser;
  const receiverUser   = chatApp.dataset.receiverUser;
  const receiverColor  = chatApp.dataset.receiverColor || "#6366f1";
  const currentColor   = chatApp.dataset.currentColor  || "#10b981";

  // ── DOM References ────────────────────────────────────────────────────────
  const messagesArea    = document.getElementById("messages-area");
  const messageInput    = document.getElementById("message-input");
  const sendBtn         = document.getElementById("send-btn");
  const statusText      = document.getElementById("status-text");
  const statusDot       = document.getElementById("status-dot");
  const connectionToast = document.getElementById("connection-toast");
  const toastText       = document.getElementById("toast-text");
  const toastDot        = document.getElementById("toast-dot");

  // ── WebSocket Connection ───────────────────────────────────────────────────
  // URL: ws://localhost:8000/ws/chat/<receiver_username>/
  // const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  // const wsUrl = `${wsScheme}://${window.location.host}/ws/chat/${receiverUser}/`;

  const wsUrl = `wss://${window.location.host}/ws/chat/${receiverUser}/`;

  let socket = null;
  let reconnectTimer = null;
  let reconnectAttempts = 0;

  function connect() {
    showToast("connecting", "Connecting…");
    socket = new WebSocket(wsUrl);

    // ── socket.onopen ──────────────────────────────────────────────────────
    socket.onopen = function () {
      console.log("[WS] Connected");
      reconnectAttempts = 0;
      showToast("connected", "Connected");
      setTimeout(hideToast, 2000);
      setStatus("online");
    };

    // ── socket.onmessage ──────────────────────────────────────────────────
    socket.onmessage = function (event) {
      const data = JSON.parse(event.data);

      if (data.type === "chat_message") {
        // A new chat message arrived
        const isSent = data.sender === currentUser;
        appendMessage({
          text:      data.message,
          sender:    data.sender,
          timestamp: data.timestamp,
          isSent:    isSent,
        });
        scrollToBottom();

      } 
      
      else if (data.type === "sidebar_update") {
        // 1. Find the sidebar item for this sender
        const userItem = document.querySelector(`.user-item[href*="${data.sender}"]`);
        if (userItem) {
            // 2. Update the preview text
            const preview = userItem.querySelector(".user-preview");
            if (preview) preview.textContent = data.message;
            
            // 3. Optional: Move to top of list
            const userList = document.querySelector(".user-list");
            userList.prepend(userItem);
        }
    }
      
      else if (data.type === "user_status") {
        // The other user went online/offline
        if (data.username === receiverUser) {
          setStatus(data.is_online ? "online" : "offline");
        }
      }
    };

    // ── socket.onclose ────────────────────────────────────────────────────
    socket.onclose = function (event) {
      console.log("[WS] Disconnected", event.code);
      showToast("disconnected", "Disconnected — reconnecting…");
      setStatus("offline");
      scheduleReconnect();
    };

    // ── socket.onerror ────────────────────────────────────────────────────
    socket.onerror = function (err) {
      console.error("[WS] Error:", err);
    };
  }

  function scheduleReconnect() {
    clearTimeout(reconnectTimer);
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
    reconnectAttempts++;
    console.log(`[WS] Reconnecting in ${delay}ms…`);
    reconnectTimer = setTimeout(connect, delay);
  }

  // ── Send Message ──────────────────────────────────────────────────────────
  function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !socket || socket.readyState !== WebSocket.OPEN) return;

    // Send JSON payload to the server
    socket.send(JSON.stringify({ message: text }));
    messageInput.value = "";
    messageInput.style.height = "auto";
    messageInput.focus();
  }

  // ── Event Listeners ───────────────────────────────────────────────────────
  sendBtn.addEventListener("click", sendMessage);

  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-grow textarea
  messageInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 120) + "px";
  });

  // ── UI Helpers ────────────────────────────────────────────────────────────

  /**
   * Creates and appends a message bubble to the chat.
   */
  function appendMessage({ text, sender, timestamp, isSent }) {
    const row = document.createElement("div");
    row.className = `message-row ${isSent ? "sent" : "received"}`;

    const color = isSent ? currentColor : receiverColor;
    const initial = sender.charAt(0).toUpperCase();

    row.innerHTML = `
      <div class="msg-avatar" style="background:${color}">${initial}</div>
      <div>
        <div class="message-bubble">${escapeHtml(text)}</div>
        <div class="msg-time">${timestamp}</div>
      </div>
    `;
    messagesArea.appendChild(row);
  }

  function scrollToBottom(smooth = true) {
    messagesArea.scrollTo({
      top: messagesArea.scrollHeight,
      behavior: smooth ? "smooth" : "auto",
    });
  }

  function setStatus(status) {
    if (!statusText || !statusDot) return;
    if (status === "online") {
      statusText.textContent = "Online";
      statusText.className = "status online";
      if (statusDot) statusDot.style.display = "block";
    } else {
      statusText.textContent = "Offline";
      statusText.className = "status";
      if (statusDot) statusDot.style.display = "none";
    }
  }

  function showToast(type, message) {
    if (!connectionToast) return;
    toastDot.className = `toast-dot ${type}`;
    toastText.textContent = message;
    connectionToast.style.display = "flex";
    connectionToast.style.opacity = "1";
  }

  function hideToast() {
    if (!connectionToast) return;
    connectionToast.style.opacity = "0";
    setTimeout(() => { connectionToast.style.display = "none"; }, 300);
  }

  function escapeHtml(text) {
    const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return text.replace(/[&<>"']/g, m => map[m]);
  }

  // ── Sidebar Search ────────────────────────────────────────────────────────
  const searchInput = document.getElementById("sidebar-search");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll(".user-item").forEach(item => {
        const name = item.querySelector(".user-name")?.textContent.toLowerCase() || "";
        item.style.display = name.includes(q) ? "flex" : "none";
      });
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  connect();
  scrollToBottom(false); // Jump to bottom on page load without animation

})();

// Session Storage

// 1. Save text before the page reloads
window.onbeforeunload = function() {
    const messageInput = document.getElementById('message-input');
    if (messageInput && messageInput.value) {
        sessionStorage.setItem('saved_message', messageInput.value);
    }
};

// 2. Restore text after the page loads
document.addEventListener("DOMContentLoaded", function() {
    const savedMessage = sessionStorage.getItem('saved_message');
    const messageInput = document.getElementById('message-input');
    
    if (savedMessage && messageInput) {
        messageInput.value = savedMessage;
        sessionStorage.removeItem('saved_message'); // Clear it so it doesn't stay forever
    }

    // 3. Set the 10-second reload timer
    setTimeout(function() {
        // Only reload if the user isn't actively typing (to be polite)
        // Or just force it:
        location.reload();
    }, 10000); 
});


// chat reload
document.addEventListener("DOMContentLoaded", function() {
    // Check if we are on a mobile screen
    if (window.innerWidth <= 768) {
        // Look at the URL. If it contains a username (meaning we aren't on the dashboard/list only), 
        // we add the 'chat-open' class to the body.
        const path = window.location.pathname;
        
        // Adjust this condition based on your URL structure (e.g., if it's /chat/username/)
        if (path.includes('/chat/')) { 
            document.body.classList.add('chat-open');
        }
    }
});