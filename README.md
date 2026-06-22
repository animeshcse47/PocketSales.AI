# PocketSales.AI — Visiting Card Digitization & Voice Notes Orchestrator

> A full-stack AI-powered system for sales teams to digitize visiting cards, store contacts intelligently, and attach transcribed voice notes — all through a modern chat interface.

**Live Demo:** https://pocketsales-ai.onrender.com  
**GitHub:** https://github.com/animeshcse47/PocketSales.AI

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Design Decisions & Approach](#design-decisions--approach)
- [Known Limitations](#known-limitations)

---

## Overview

PocketSales.AI solves a real problem for field sales teams — the manual effort of transcribing business card details and notes after meetings. A salesperson can:

1. Upload a photo of any visiting card
2. Have the AI extract all contact details instantly
3. Confirm or reject the extracted data (human-in-the-loop)
4. Auto-save the contact to Google Sheets with duplicate detection
5. Receive a WhatsApp notification to the manager on every new contact
6. Record a voice note about the contact — transcribed and attached to the same row in Sheets

All interactions happen through a persistent chat interface with full session history.

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React 18 + Vite + TailwindCSS | Fast, component-driven UI with hot reload |
| Backend | FastAPI (Python 3.11) | Async-first, auto-docs, production-grade |
| AI Agent | LangGraph (StateGraph) | Orchestrates multi-step agentic workflows |
| Vision + Audio AI | Google Gemini 2.5 Flash | Multimodal — handles both images and audio |
| Primary Database | Google Sheets via gspread | Accessible to non-technical stakeholders |
| Session Database | MongoDB Atlas via motor | Async, schemaless, free tier |
| File Storage | MongoDB GridFS | No extra cloud bucket needed |
| Notifications | Twilio WhatsApp API | Simple, reliable sandbox for demos |
| Deployment | Railway (backend) + Render (frontend) | Free tier, no cold starts on Railway |

---

## Architecture

```
┌─────────────────────────────────┐
│        React Frontend           │
│  ChatWindow · Sidebar · Modals  │
└────────────┬────────────────────┘
             │ HTTP (Axios)
┌────────────▼────────────────────┐
│        FastAPI Backend          │
│  /api/chat  /api/upload         │
│  /api/sessions  /api/audio      │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│      LangGraph Agent            │
│                                 │
│  router → extract_card          │
│        → confirmation           │
│        → dedup_check            │
│        → write_sheets           │
│        → send_whatsapp          │
│        → transcribe_audio       │
│        → upload_audio           │
│        → update_sheets_voice    │
│        → respond                │
└──────┬──────────┬───────────────┘
       │          │
┌──────▼──┐  ┌───▼──────────┐  ┌──────────────┐
│ MongoDB  │  │ Google Sheets │  │   Twilio     │
│ Sessions │  │   Contacts    │  │  WhatsApp    │
│ Messages │  │   (Main DB)   │  │ Notification │
│ GridFS   │  └───────────────┘  └──────────────┘
└──────────┘
```

---

## Features

### Core
- **Card Image Upload** — Upload any JPG/PNG/WebP visiting card photo
- **Gemini Vision Extraction** — AI reads and parses all contact fields (name, phone, email, company, designation, address, website)
- **Human-in-the-Loop Confirmation** — Modal shows extracted data; user confirms or retries before anything is saved
- **Deduplication** — Checks existing Sheets rows by email AND normalized phone number; blocks duplicate entries
- **Google Sheets Integration** — Writes a new row with 13 columns on confirmation; updates voice note columns later
- **WhatsApp Notification** — Sends formatted message to manager's number via Twilio sandbox on every new contact
- **Voice Note Upload** — Upload MP3/WAV/WebM audio after saving a contact
- **Audio Transcription** — Gemini transcribes the audio to text
- **GridFS Storage** — Audio stored in MongoDB, served via `/api/audio/{id}`
- **Sheets Update** — Contact row updated with transcript text and audio URL

### UX
- **Persistent Sessions** — All conversations stored in MongoDB; full history restored on session switch
- **Session Management** — Create new sessions, delete old ones (hover to reveal delete button)
- **Drag & Drop** — Drag image or audio files directly onto the input area
- **Auto-resizing Input** — Textarea grows with content up to 3 lines
- **Toast Notifications** — Contextual status messages for every operation
- **Dark Theme UI** — Material Design 3 token-based color system

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the repo

```bash
git clone https://github.com/animeshcse47/PocketSales.AI.git
cd PocketSales.AI
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment on a specific drive (recommended)
python -m venv ../venv

# Activate
..\venv\Scripts\activate          # Windows
# source ../venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in your credentials (see Environment Variables section)
```

### 3. Run the backend

```bash
# From the backend/ directory with venv active
uvicorn app.main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 4. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

### 5. Run the frontend

```bash
npm run dev
```

Visit: `http://localhost:5173`

### 6. Docker (optional)

```bash
# From project root
docker-compose up --build
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key from [Google AI Studio](https://aistudio.google.com) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full service account JSON as a single-line string |
| `GOOGLE_SHEET_ID` | ID from your Google Sheet URL |
| `GOOGLE_SHEET_NAME` | Tab name inside the sheet (default: `Contacts`) |
| `GOOGLE_DRIVE_FOLDER_ID` | Drive folder ID shared with service account (optional) |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `WHATSAPP_PROVIDER` | `twilio` or `meta` |
| `TWILIO_ACCOUNT_SID` | From Twilio Console |
| `TWILIO_AUTH_TOKEN` | From Twilio Console |
| `TWILIO_WHATSAPP_NUMBER` | Twilio sandbox number: `whatsapp:+14155238886` |
| `MANAGER_WHATSAPP_NUMBER` | Number that receives new contact alerts (must join sandbox first) |
| `BACKEND_PUBLIC_URL` | Full backend URL for audio file links |
| `FRONTEND_URL` | Frontend URL for CORS whitelist |
| `SECRET_KEY` | Random string for security |
| `ENVIRONMENT` | `development` or `production` |

### Google Sheet Setup

1. Create a new Google Sheet
2. Share it with your service account's `client_email` — give **Editor** access
3. The app automatically creates the **Contacts** tab with these headers on first run:

`ID | Name | Phone | Email | Company | Designation | Address | Website | LinkedIn | Voice Note URL | Voice Transcript | Session ID | Logged At`

### Twilio WhatsApp Sandbox Setup

1. Go to Twilio Console → Messaging → Try WhatsApp
2. From the manager's phone, send the sandbox join code (e.g. `join material-warm`) to `+1 415 523 8886` on WhatsApp
3. The number is now a sandbox participant and will receive notifications

---

## Project Structure

```
PocketSales.AI/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py        # LangGraph StateGraph definition
│   │   │   ├── nodes.py        # All 9 graph node functions
│   │   │   └── state.py        # AgentState TypedDict
│   │   ├── api/
│   │   │   ├── chat.py         # POST /api/chat — manual graph runner
│   │   │   ├── upload.py       # POST /api/upload/image|audio
│   │   │   ├── sessions.py     # CRUD /api/sessions
│   │   │   └── audio.py        # GET /api/audio/{id} — GridFS streaming
│   │   ├── models/
│   │   │   ├── contact.py      # ContactCard, ContactRecord
│   │   │   ├── session.py      # ChatSession
│   │   │   └── message.py      # ChatMessage
│   │   ├── services/
│   │   │   ├── vision_service.py    # Gemini image → ContactCard
│   │   │   ├── audio_service.py     # Gemini audio → transcript
│   │   │   ├── sheets_service.py    # gspread read/write/dedup
│   │   │   ├── storage_service.py   # MongoDB GridFS upload
│   │   │   ├── whatsapp_service.py  # Twilio/Meta notification
│   │   │   └── mongo_service.py     # Session + message CRUD
│   │   ├── config.py           # Pydantic settings from .env
│   │   └── main.py             # FastAPI app + CORS
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatWindow.jsx       # Main chat UI + input bar
│       │   ├── MessageBubble.jsx    # Renders user/AI messages
│       │   ├── ContactCard.jsx      # Extracted card preview
│       │   ├── ConfirmationModal.jsx # Human-in-the-loop dialog
│       │   ├── FileUploader.jsx     # Upload buttons + drag & drop
│       │   ├── SessionSidebar.jsx   # Session list + delete
│       │   └── Toast.jsx            # Status notifications
│       ├── hooks/
│       │   ├── useChat.js           # Message state + API calls
│       │   └── useSession.js        # Session load/create/switch
│       └── services/
│           └── api.js               # Axios wrapper for all endpoints
├── docker-compose.yml
└── README.md
```

---

## Design Decisions & Approach

### Why LangGraph?
The card digitization workflow is inherently a multi-step, stateful process — not a single API call. LangGraph's `StateGraph` lets each step (extract → confirm → dedup → write → notify) be a separate node with conditional routing between them. This makes the flow transparent, testable, and easy to extend (e.g. adding an enrichment step).

One key challenge: LangGraph's `MemorySaver` checkpointer tries to serialize the entire state to JSON, but raw image/audio bytes are not JSON-serializable. The solution was to run the graph nodes manually in sequence (bypassing the checkpointer for in-flight byte data) while still persisting session state in MongoDB between HTTP requests.

### Why Google Sheets as the primary database?
The assignment specified Sheets as the main contact store. It also makes practical sense for sales teams — managers can open the sheet directly without any special tooling. The service account approach (rather than OAuth) allows server-side writes without user interaction.

### Why MongoDB GridFS for audio?
Google Cloud Storage requires billing and service account storage quota. Google Drive API doesn't allow service accounts to own files in personal drives. GridFS stores binary files directly in the existing MongoDB Atlas cluster — zero additional infrastructure, free tier, and the audio is served back through the FastAPI backend via a streaming endpoint.

### Human-in-the-Loop
After card extraction, the agent sets `awaiting_confirmation=True` and saves the extracted contact to MongoDB session state. The frontend shows a confirmation modal. On the next request, the backend loads the pending contact from MongoDB and routes to the dedup/write pipeline only if confirmed. This survives page refreshes and network interruptions.

### Deduplication
Matches on email (case-insensitive) OR phone number (digits only, normalized). This handles formatting differences like `+91 99999-00000` vs `9999900000`.

---

## Known Limitations

- **Twilio Sandbox** — WhatsApp notifications use the Twilio sandbox which requires each recipient to opt in once. A production deployment would need a Twilio-approved WhatsApp Business number.
- **Render Free Tier Sleep** — The frontend on Render's free static site tier doesn't sleep, but the Railway backend on free tier may have resource limits under sustained load.
- **Gemini Rate Limits** — The Gemini API key used is a free tier key with per-minute rate limits. Under heavy concurrent usage, requests may be throttled.
- **In-Memory File Store** — Uploaded files (image/audio bytes) are held in a Python dict between the upload and chat endpoints. This works for single-instance deployments but would need Redis in a multi-instance setup.
- **gspread Sync** — The Google Sheets library (`gspread`) is synchronous. All sheet operations run in a thread pool executor to avoid blocking the async event loop, which adds minor latency.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/sessions/` | Create new session |
| `GET` | `/api/sessions/` | List all sessions |
| `DELETE` | `/api/sessions/{id}` | Delete session + messages |
| `POST` | `/api/chat/` | Send message / process upload |
| `GET` | `/api/chat/{id}/history` | Get session message history |
| `POST` | `/api/upload/image` | Upload card image, get ref key |
| `POST` | `/api/upload/audio` | Upload voice note, get ref key |
| `GET` | `/api/audio/{file_id}` | Stream audio from GridFS |

Full interactive docs: `http://localhost:8000/docs`
