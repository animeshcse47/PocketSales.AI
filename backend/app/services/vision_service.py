import base64
import json
import google.generativeai as genai
from app.config import settings
from app.models.contact import ContactCard

genai.configure(api_key=settings.google_api_key)

EXTRACTION_PROMPT = """You are an expert at reading visiting/business cards.
Extract all contact information from this card image.

Return ONLY a valid JSON object with these exact fields (use null for missing fields):
{
  "name": "Full name on the card",
  "phone": "Phone number(s), comma-separated if multiple",
  "email": "Email address",
  "company": "Company or organization name",
  "designation": "Job title or role",
  "address": "Physical address if present",
  "website": "Website URL if present",
  "raw_text": "All text visible on the card verbatim"
}

Rules:
- Return ONLY the JSON object, no markdown, no explanation
- If the image is not a visiting card, return {"error": "Not a valid visiting card"}"""


async def extract_card_data(image_bytes: bytes, mime_type: str = "image/jpeg") -> ContactCard:
    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content([
        EXTRACTION_PROMPT,
        {"mime_type": mime_type, "data": image_bytes}
    ])

    raw = response.text.strip()

    # strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        raw = "\n".join(lines).strip()

    data = json.loads(raw)

    if "error" in data:
        raise ValueError(data["error"])

    return ContactCard(**data)
