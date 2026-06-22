from fastapi import APIRouter, HTTPException
from app.services.mongo_service import create_session, get_all_sessions, get_session, delete_session

router = APIRouter()


@router.post("/")
async def new_session():
    session = await create_session()
    return session.model_dump()


@router.get("/")
async def list_sessions():
    sessions = await get_all_sessions()
    return {"sessions": [s.model_dump() for s in sessions]}


@router.get("/{session_id}")
async def get_session_detail(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session.model_dump()


@router.delete("/{session_id}")
async def remove_session(session_id: str):
    await delete_session(session_id)
    return {"ok": True}
