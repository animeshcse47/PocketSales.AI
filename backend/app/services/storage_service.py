import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from app.services.mongo_service import _db
from app.config import settings


async def upload_audio_file(audio_bytes: bytes, session_id: str, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    unique_name = f"{session_id[:8]}_{uuid.uuid4().hex[:6]}.{ext}"

    bucket = AsyncIOMotorGridFSBucket(_db, bucket_name="audio_files")
    file_id = await bucket.upload_from_stream(
        unique_name,
        audio_bytes,
        metadata={
            "session_id": session_id,
            "original_filename": filename,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    )

    base_url = settings.backend_public_url.rstrip("/")
    return f"{base_url}/api/audio/{file_id}"
