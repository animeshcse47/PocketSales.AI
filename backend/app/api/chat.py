from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.nodes import (
    router_node, extract_card_node, confirmation_node, dedup_check_node,
    write_sheets_node, whatsapp_node, transcribe_audio_node,
    upload_audio_node, update_sheets_voice_node, respond_node,
)
from app.agent.state import AgentState
from app.models.message import ChatMessage
from app.services.mongo_service import (
    add_message,
    get_messages,
    get_session,
    update_session,
)

router = APIRouter()

_file_store: dict = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    image_ref: Optional[str] = None
    audio_ref: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    response_type: str
    metadata: Optional[dict] = None


async def _run_graph(state: AgentState) -> tuple[AgentState, str]:
    """
    Runs the agent graph manually, avoiding LangGraph checkpointer
    which cannot serialize bytes. Returns (final_state, intent).
    """
    state = await router_node(state)
    intent = state.get("intent", "TEXT_MESSAGE")

    if intent == "IMAGE_UPLOAD":
        state = await extract_card_node(state)
        state = {**state, "image_bytes": None, "audio_bytes": None}

        # save the extracted contact + awaiting flag to mongo NOW
        # so the next confirmation request can load it back
        if state.get("extracted_contact"):
            await update_session(
                state["session_id"],
                last_contact=state["extracted_contact"],
                awaiting_confirmation=True,
            )

        state = await respond_node(state)

    elif intent == "VOICE_UPLOAD":
        state = await transcribe_audio_node(state)
        if not state.get("error"):
            state = await upload_audio_node(state)
        if not state.get("error"):
            state = await update_sheets_voice_node(state)
        state = {**state, "image_bytes": None, "audio_bytes": None}
        await update_session(state["session_id"], awaiting_confirmation=False)
        state = await respond_node(state)

    elif intent in ("CONFIRMATION_YES", "CONFIRMATION_NO"):
        state = await confirmation_node(state)
        if state.get("user_confirmed"):
            state = await dedup_check_node(state)
            if not state.get("is_duplicate"):
                state = await write_sheets_node(state)
                state = await whatsapp_node(state)
        await update_session(state["session_id"], awaiting_confirmation=False)
        state = await respond_node(state)

    else:
        state = await respond_node(state)

    return state, intent


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session = await get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    image_bytes = _file_store.pop(request.image_ref, None) if request.image_ref else None
    audio_bytes = _file_store.pop(request.audio_ref, None) if request.audio_ref else None
    audio_filename = _file_store.pop(f"{request.audio_ref}_filename", "audio.webm") if request.audio_ref else "audio.webm"
    image_mime = _file_store.pop(f"{request.image_ref}_mime", "image/jpeg") if request.image_ref else "image/jpeg"

    # load extracted contact from session for confirmation turns
    pending_contact = session.last_contact if session.awaiting_confirmation else None

    state: AgentState = {
        "session_id": request.session_id,
        "messages": [],
        "user_text": request.message,
        "image_bytes": image_bytes,
        "image_mime_type": image_mime,
        "audio_bytes": audio_bytes,
        "audio_filename": audio_filename,
        "intent": None,
        "extracted_contact": pending_contact,
        "awaiting_confirmation": session.awaiting_confirmation,
        "user_confirmed": None,
        "is_duplicate": False,
        "duplicate_row": None,
        "written_row": None,
        "audio_transcript": None,
        "audio_url": None,
        "response_message": None,
        "response_type": None,
        "response_metadata": None,
        "error": None,
    }

    result, intent = await _run_graph(state)

    user_label = request.message
    if image_bytes:
        user_label = "📷 Card image uploaded"
    elif audio_bytes:
        user_label = "🎙️ Voice note uploaded"

    await add_message(request.session_id, ChatMessage(
        role="user",
        content=user_label,
        timestamp=datetime.utcnow()
    ))
    await add_message(request.session_id, ChatMessage(
        role="assistant",
        content=result.get("response_message", ""),
        message_type=result.get("response_type", "text"),
        metadata=result.get("response_metadata"),
        timestamp=datetime.utcnow()
    ))

    return ChatResponse(
        session_id=request.session_id,
        response=result.get("response_message", ""),
        response_type=result.get("response_type", "text"),
        metadata=result.get("response_metadata"),
    )


@router.get("/{session_id}/history")
async def get_history(session_id: str):
    messages = await get_messages(session_id)
    return {"messages": [m.model_dump() for m in messages]}


def get_file_store() -> dict:
    return _file_store
