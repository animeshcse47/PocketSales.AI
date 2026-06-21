from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    message_type: Literal["text", "image", "audio", "card_preview", "confirmation"] = "text"
    file_url: Optional[str] = None
    metadata: Optional[dict] = None
    timestamp: datetime = datetime.utcnow()
