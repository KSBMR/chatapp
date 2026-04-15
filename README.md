# 💬 Django Chat App

A **WhatsApp-style real-time chat application** built with Django, Django Channels, and WebSockets.

---

## ✨ Features

- 🔐 **User Authentication** — Register, Login, Logout
- 💬 **Real-time Messaging** — WebSocket-powered instant messaging
- 👥 **User List** — See all users, start a conversation instantly
- 📜 **Chat History** — Persistent messages stored in SQLite
- 🟢 **Online Status** — See who's online in real time
- 🔔 **Unread Badges** — Unread message counts per conversation
- 👤 **User Profile** — View your stats (sent/received messages)
- 🎨 **Modern Dark UI** — Clean, responsive design with no Bootstrap dependency
- 🛠️ **Admin Panel** — Manage users and messages at `/admin/`

---

## 🛠️ Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python 3.10+, Django 4.2          |
| Real-time   | Django Channels 4, Daphne (ASGI)  |
| WebSocket   | channels.generic.websocket        |
| Database    | SQLite (default, zero config)     |
| Frontend    | Vanilla HTML, CSS, JavaScript     |
| Fonts       | Google Fonts (DM Sans + Syne)     |

---

## 📁 Project Structure

```
django_chat_app/
│
├── django_chat_app/          # Project configuration package
│   ├── __init__.py
│   ├── asgi.py               # ASGI entry point (HTTP + WebSocket routing)
│   ├── settings.py           # Django settings (Channels, DB, etc.)
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI entry (not used for real-time)
│
├── chat/                     # Main application
│   ├── migrations/           # Database migrations
│   ├── static/
│   │   ├── css/style.css     # All styles (dark theme)
│   │   └── js/chat.js        # WebSocket client logic
│   ├── templates/chat/
│   │   ├── login.html        # Login page
│   │   ├── register.html     # Registration page
│   │   ├── dashboard.html    # User list / home page
│   │   ├── chat.html         # One-to-one chat interface
│   │   └── profile.html      # User profile page
│   ├── admin.py              # Admin panel config
│   ├── apps.py
│   ├── consumers.py          # WebSocket consumer (real-time logic)
│   ├── forms.py              # RegisterForm, LoginForm
│   ├── models.py             # Message, UserProfile models
│   ├── routing.py            # WebSocket URL routing
│   ├── urls.py               # HTTP URL patterns
│   └── views.py              # All view functions
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone / Download the project

```bash
# If using git
git clone <your-repo-url>
cd django_chat_app

# Or just cd into the folder
cd django_chat_app
```

### 2. Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (for admin panel)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

> **Important:** Daphne (ASGI server) is configured automatically through Django's `ASGI_APPLICATION` setting and the `daphne` entry in `INSTALLED_APPS`. The standard `runserver` command will use Daphne for WebSocket support.

### 7. Open the app

| URL                          | Purpose                  |
|------------------------------|--------------------------|
| http://127.0.0.1:8000/       | Dashboard (redirect)     |
| http://127.0.0.1:8000/login/ | Login                    |
| http://127.0.0.1:8000/register/ | Register              |
| http://127.0.0.1:8000/dashboard/ | User list            |
| http://127.0.0.1:8000/chat/username/ | Chat with user   |
| http://127.0.0.1:8000/admin/ | Admin panel              |

---

## 🔌 How WebSocket Works

```
Browser                         Django Server (Daphne ASGI)
  │                                       │
  │──── HTTP GET /chat/alice/ ───────────▶│  (Django view renders chat.html)
  │◀─── HTML page with JS ───────────────│
  │                                       │
  │──── WS CONNECT /ws/chat/alice/ ─────▶│  consumers.py → connect()
  │                                       │    • Joins room group "chat_alice_bob"
  │                                       │    • Marks user online
  │◀─── WS OPEN ─────────────────────────│
  │                                       │
  │──── WS SEND {"message":"Hello!"} ───▶│  consumers.py → receive()
  │                                       │    • Saves message to DB
  │                                       │    • group_send to "chat_alice_bob"
  │                                       │
  │◀─── WS MESSAGE {"type":"chat_message",│  consumers.py → chat_message()
  │      "message":"Hello!",              │    • Forwards event to WebSocket
  │      "sender":"bob",                  │
  │      "timestamp":"14:32"} ───────────│
  │                                       │
  │ (JS appends bubble to chat window)    │
  │                                       │
  │──── WS CLOSE ────────────────────────▶│  consumers.py → disconnect()
  │                                       │    • Leaves room group
  │                                       │    • Marks user offline
```

### Key Components

| File              | Role                                                   |
|-------------------|--------------------------------------------------------|
| `asgi.py`         | Routes HTTP → Django, WebSocket → Channels             |
| `routing.py`      | Maps `/ws/chat/<username>/` to `ChatConsumer`          |
| `consumers.py`    | Handles connect / receive / disconnect events          |
| `chat.js`         | Opens WebSocket, sends messages, renders bubbles       |
| `settings.py`     | Configures `CHANNEL_LAYERS` (InMemory for dev)        |

---

## ⚙️ Configuration Notes

### Channel Layer (settings.py)

For **development** (default, zero config):
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}
```

For **production** (requires Redis):
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    }
}
```

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set a strong `SECRET_KEY` (use environment variable)
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Switch to Redis channel layer
- [ ] Run `python manage.py collectstatic`
- [ ] Use a production database (PostgreSQL recommended)
- [ ] Serve with Daphne behind Nginx

---

## 🎨 UI Highlights

- **Dark luxury theme** with emerald green accents
- **Syne** display font for headings
- **DM Sans** for body text
- Smooth message animations
- Real-time online/offline status dot
- Connection toast (connecting / connected / disconnected)
- Responsive sidebar with user search
- Unread message badges

---

## 📝 Database Models

### Message
| Field       | Type          | Description                  |
|-------------|---------------|------------------------------|
| sender      | ForeignKey    | User who sent the message    |
| receiver    | ForeignKey    | User who received it         |
| message     | TextField     | Message content              |
| timestamp   | DateTimeField | When it was sent             |
| is_read     | BooleanField  | Whether it has been read     |

### UserProfile
| Field        | Type          | Description                    |
|--------------|---------------|--------------------------------|
| user         | OneToOneField | Link to Django's User model    |
| is_online    | BooleanField  | Current online status          |
| last_seen    | DateTimeField | Last seen timestamp            |
| avatar_color | CharField     | Hex color for avatar           |

---

## 🧩 Testing the App

1. Register two users (e.g., `alice` and `bob`)
2. Open two browser tabs / windows (or use incognito for the second)
3. Log in as `alice` in one tab, `bob` in the other
4. Click on each other's name in the sidebar
5. Type a message — it appears instantly in both windows! ⚡

---

## 📄 License

MIT — use freely for learning and personal projects.
