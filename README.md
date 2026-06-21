# PocketSales.AI — Visiting Card Digitizer & Voice Notes Orchestrator

An AI-powered full-stack system for sales teams to digitize visiting cards via chat, store contacts in Google Sheets, and attach transcribed voice notes — all through a modern chat interface.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TailwindCSS |
| Backend | FastAPI + LangGraph |
| AI (Vision + Audio) | Google Gemini 2.5 Flash |
| Primary DB | Google Sheets (via gspread) |
| Session DB | MongoDB Atlas |
| File Storage | MongoDB GridFS |
| Notifications | Twilio WhatsApp API |
| Containerization | Docker + docker-compose |

## How It Works

1. Salesperson uploads a visiting card photo in the chat
2. Gemini Vision extracts all contact fields (name, phone, email, company, etc.)
3. Extracted card is shown — user confirms or retries (human-in-the-loop)
4. System checks Google Sheets for duplicates by email + phone
5. If unique, contact is saved to Sheets and WhatsApp notification sent to manager
6. Salesperson uploads a voice note — Gemini transcribes it, audio stored in MongoDB
7. Contact row in Sheets is updated with transcript + audio URL
8. All sessions and messages persist in MongoDB Atlas

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas cluster
- Google Cloud service account with Sheets + Drive API enabled
- Twilio account with WhatsApp sandbox

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` — API docs at `http://localhost:8000/docs`

### Docker

```bash
docker-compose up --build
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key from Google AI Studio |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full service account JSON (stringified) |
| `GOOGLE_SHEET_ID` | ID from your Google Sheet URL |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `TWILIO_ACCOUNT_SID` | From Twilio Console |
| `TWILIO_AUTH_TOKEN` | From Twilio Console |
| `TWILIO_WHATSAPP_NUMBER` | Your Twilio WhatsApp sender number |
| `MANAGER_WHATSAPP_NUMBER` | Number that receives new contact alerts |

## Google Sheet Setup

1. Create a new Google Sheet
2. Share it with your service account email (found as `client_email` in your service account JSON) — give **Editor** access
3. Paste the Sheet ID into `GOOGLE_SHEET_ID` in `.env`
4. The app auto-creates the **Contacts** tab with headers on first run

## Project Structure

```
visiting-card-digitizer/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph StateGraph + nodes
│   │   ├── api/            # FastAPI routes
│   │   ├── models/         # Pydantic models
│   │   └── services/       # Gemini, Sheets, MongoDB, WhatsApp
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/     # React UI components
│       ├── hooks/          # useChat, useSession
│       └── services/       # Axios API client
└── docker-compose.yml
```
