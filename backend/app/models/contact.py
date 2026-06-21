from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContactCard(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    raw_text: Optional[str] = None


class ContactRecord(ContactCard):
    id: Optional[str] = None
    sheet_row: Optional[int] = None
    voice_note_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    logged_at: datetime = datetime.utcnow()
    session_id: Optional[str] = None
