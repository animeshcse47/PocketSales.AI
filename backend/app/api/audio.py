from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from app.services.mongo_service import _db

router = APIRouter()


@router.get("/{file_id}")
async def get_audio(file_id: str):
    try:
        bucket = AsyncIOMotorGridFSBucket(_db, bucket_name="audio_files")
        oid = ObjectId(file_id)

        grid_out = await bucket.open_download_stream(oid)

        async def stream():
            while True:
                chunk = await grid_out.read(65536)
                if not chunk:
                    break
                yield chunk

        filename = grid_out.filename or "audio.webm"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
        mime_map = {
            "mp3": "audio/mpeg", "wav": "audio/wav",
            "webm": "audio/webm", "ogg": "audio/ogg",
            "mp4": "audio/mp4", "m4a": "audio/mp4",
        }
        content_type = mime_map.get(ext, "audio/webm")

        return StreamingResponse(
            stream(),
            media_type=content_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Audio not found: {e}")
