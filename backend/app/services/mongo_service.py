import uuid
from datetime import datetime
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.message import ChatMessage
from app.models.session import ChatSession

_client = AsyncIOMotorClient(settings.mongodb_uri)
_db = _client["carddb"]
sessions_col = _db["sessions"]
messages_col = _db["messages"]


async def create_session() -> ChatSession:
    session = ChatSession(session_id=str(uuid.uuid4()))
    await sessions_col.insert_one(session.model_dump())
    return session


async def get_session(session_id: str) -> Optional[ChatSession]:
    doc = await sessions_col.find_one({"session_id": session_id})
    if not doc:
        return None
    doc.pop("_id", None)
    return ChatSession(**doc)


async def get_all_sessions() -> List[ChatSession]:
    cursor = sessions_col.find().sort("last_active", -1).limit(50)
    docs = await cursor.to_list(length=50)
    result = []
    for doc in docs:
        doc.pop("_id", None)
        result.append(ChatSession(**doc))
    return result


async def update_session(session_id: str, **kwargs):
    kwargs["last_active"] = datetime.utcnow()
    await sessions_col.update_one(
        {"session_id": session_id},
        {"$set": kwargs}
    )


async def delete_session(session_id: str):
    await sessions_col.delete_one({"session_id": session_id})
    await messages_col.delete_many({"session_id": session_id})


async def add_message(session_id: str, message: ChatMessage):
    doc = message.model_dump()
    doc["session_id"] = session_id
    await messages_col.insert_one(doc)


async def get_messages(session_id: str) -> List[ChatMessage]:
    cursor = messages_col.find({"session_id": session_id}).sort("timestamp", 1)
    docs = await cursor.to_list(length=200)
    result = []
    for doc in docs:
        doc.pop("_id", None)
        doc.pop("session_id", None)
        result.append(ChatMessage(**doc))
    return result
