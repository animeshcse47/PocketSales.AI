from typing import TypedDict, Optional, List, Literal


class AgentState(TypedDict):
    session_id: str
    messages: List[dict]

    user_text: Optional[str]
    image_bytes: Optional[bytes]
    image_mime_type: Optional[str]
    audio_bytes: Optional[bytes]
    audio_filename: Optional[str]

    intent: Optional[Literal[
        "IMAGE_UPLOAD",
        "VOICE_UPLOAD",
        "TEXT_MESSAGE",
        "CONFIRMATION_YES",
        "CONFIRMATION_NO"
    ]]

    extracted_contact: Optional[dict]

    awaiting_confirmation: bool
    user_confirmed: Optional[bool]

    is_duplicate: bool
    duplicate_row: Optional[int]
    written_row: Optional[int]

    audio_transcript: Optional[str]
    audio_url: Optional[str]

    response_message: Optional[str]
    response_type: Optional[str]
    response_metadata: Optional[dict]

    error: Optional[str]
