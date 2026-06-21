import io
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.google_api_key)


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"

    mime_map = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "webm": "audio/webm",
        "ogg": "audio/ogg",
        "mp4": "audio/mp4",
        "m4a": "audio/mp4",
    }
    mime_type = mime_map.get(ext, "audio/webm")

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content([
        "Transcribe the following audio recording accurately. Return only the transcript text, nothing else.",
        {"mime_type": mime_type, "data": audio_bytes}
    ])

    return response.text.strip()
