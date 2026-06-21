from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import chat, upload, sessions, audio

app = FastAPI(
    title="Visiting Card Digitizer API",
    description="AI-powered visiting card processing with LangGraph + Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
