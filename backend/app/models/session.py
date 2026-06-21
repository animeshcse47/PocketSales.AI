from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatSession(BaseModel):
    session_id: str
    created_at: datetime = datetime.utcnow()
    last_active: datetime = datetime.utcnow()
    last_contact: Optional[dict] = None
    last_sheet_row: Optional[int] = None
    title: Optional[str] = "New Session"
    awaiting_confirmation: bool = False
