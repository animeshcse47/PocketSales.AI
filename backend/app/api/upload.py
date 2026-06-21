import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.chat import get_file_store

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/webm", "audio/ogg",
                       "audio/mp4", "audio/x-m4a", "video/webm"}


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, f"Unsupported image type: {file.content_type}")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image too large — max 10MB")

    ref = str(uuid.uuid4())
    store = get_file_store()
    store[ref] = contents
    store[f"{ref}_mime"] = file.content_type or "image/jpeg"

    return {"ref": ref, "filename": file.filename, "size": len(contents)}


@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(400, f"Unsupported audio type: {file.content_type}")

    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(400, "Audio too large — max 25MB")

    ref = str(uuid.uuid4())
    store = get_file_store()
    store[ref] = contents
    store[f"{ref}_filename"] = file.filename or "audio.webm"

    return {"ref": ref, "filename": file.filename, "size": len(contents)}
