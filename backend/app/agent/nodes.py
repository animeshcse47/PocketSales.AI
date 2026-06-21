import logging
from app.agent.state import AgentState
from app.models.contact import ContactCard

logger = logging.getLogger(__name__)


async def router_node(state: AgentState) -> AgentState:
    if state.get("awaiting_confirmation"):
        text = (state.get("user_text") or "").lower().strip()
        yes_words = ["yes", "correct", "confirm", "ok", "sure", "yep", "right", "looks good"]
        no_words = ["no", "wrong", "incorrect", "edit", "change", "fix", "retry", "redo"]
        if any(w in text for w in yes_words):
            return {**state, "intent": "CONFIRMATION_YES"}
        elif any(w in text for w in no_words):
            return {**state, "intent": "CONFIRMATION_NO"}

    if state.get("image_bytes"):
        return {**state, "intent": "IMAGE_UPLOAD"}
    if state.get("audio_bytes"):
        return {**state, "intent": "VOICE_UPLOAD"}

    return {**state, "intent": "TEXT_MESSAGE"}


async def extract_card_node(state: AgentState) -> AgentState:
    from app.services.vision_service import extract_card_data

    try:
        contact = await extract_card_data(
            state["image_bytes"],
            state.get("image_mime_type", "image/jpeg")
        )
        return {
            **state,
            "extracted_contact": contact.model_dump(),
            "response_message": "I've extracted the contact details from the card. Please confirm if everything looks correct:",
            "response_type": "card_preview",
            "response_metadata": contact.model_dump(),
            "awaiting_confirmation": True,
            "error": None,
        }
    except ValueError as e:
        return {
            **state,
            "error": str(e),
            "response_message": f"⚠️ Couldn't read this as a visiting card — try a clearer image.",
            "response_type": "text",
            "awaiting_confirmation": False,
        }
    except Exception as e:
        logger.error(f"Vision extraction error: {e}")
        return {
            **state,
            "error": str(e),
            "response_message": "❌ Something went wrong processing the image. Please try again.",
            "response_type": "text",
        }


async def confirmation_node(state: AgentState) -> AgentState:
    if state["intent"] == "CONFIRMATION_YES":
        return {**state, "user_confirmed": True, "awaiting_confirmation": False}

    return {
        **state,
        "user_confirmed": False,
        "awaiting_confirmation": False,
        "extracted_contact": None,
        "response_message": "No problem — upload the card again and I'll re-extract the details.",
        "response_type": "text",
    }


async def dedup_check_node(state: AgentState) -> AgentState:
    from app.services.sheets_service import check_duplicate

    try:
        contact = ContactCard(**state["extracted_contact"])
        is_dup, dup_row = await check_duplicate(contact)

        if is_dup:
            return {
                **state,
                "is_duplicate": True,
                "duplicate_row": dup_row,
                "response_message": (
                    f"⚠️ **{contact.name}** from **{contact.company}** already exists in your database. "
                    f"No duplicate entry created."
                ),
                "response_type": "text",
            }

        return {**state, "is_duplicate": False, "duplicate_row": None}

    except Exception as e:
        logger.error(f"Dedup check error: {e}")
        return {**state, "is_duplicate": False, "error": str(e)}


async def write_sheets_node(state: AgentState) -> AgentState:
    from app.services.sheets_service import write_contact
    from app.services.mongo_service import update_session

    try:
        contact = ContactCard(**state["extracted_contact"])
        row_number = await write_contact(contact, state["session_id"])

        await update_session(
            state["session_id"],
            last_contact=state["extracted_contact"],
            last_sheet_row=row_number,
            title=contact.name or "Unknown Contact",
        )

        return {
            **state,
            "written_row": row_number,
            "response_message": (
                f"✅ **{contact.name}** from **{contact.company or 'Unknown Company'}** "
                f"has been saved to Google Sheets!\n\n"
                f"📢 Sending WhatsApp notification to your manager...\n\n"
                f"💡 You can now upload a voice note about this contact."
            ),
            "response_type": "text",
        }

    except Exception as e:
        logger.error(f"Sheets write error: {e}")
        return {
            **state,
            "error": str(e),
            "response_message": f"❌ Failed to save contact: {str(e)}",
            "response_type": "text",
        }


async def whatsapp_node(state: AgentState) -> AgentState:
    from app.services.whatsapp_service import send_whatsapp_notification

    try:
        contact = ContactCard(**state["extracted_contact"])
        await send_whatsapp_notification(contact)
    except Exception as e:
        logger.error(f"WhatsApp notification failed: {e}")

    return state


async def transcribe_audio_node(state: AgentState) -> AgentState:
    from app.services.audio_service import transcribe_audio

    try:
        transcript = await transcribe_audio(
            state["audio_bytes"],
            state.get("audio_filename", "audio.webm")
        )
        return {**state, "audio_transcript": transcript}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {
            **state,
            "error": str(e),
            "response_message": "❌ Failed to transcribe the voice note. Please try again.",
            "response_type": "text",
        }


async def upload_audio_node(state: AgentState) -> AgentState:
    from app.services.storage_service import upload_audio_file

    try:
        url = await upload_audio_file(
            state["audio_bytes"],
            state["session_id"],
            state.get("audio_filename", "voice.webm")
        )
        return {**state, "audio_url": url}
    except Exception as e:
        logger.error(f"GCS upload error: {e}")
        return {
            **state,
            "error": str(e),
            "response_message": "❌ Failed to upload the audio file. Please try again.",
            "response_type": "text",
        }


async def update_sheets_voice_node(state: AgentState) -> AgentState:
    from app.services.sheets_service import update_voice_note
    from app.services.mongo_service import get_session

    session = await get_session(state["session_id"])
    row_to_update = session.last_sheet_row if session else state.get("written_row")

    if not row_to_update:
        return {
            **state,
            "response_message": (
                "⚠️ No recently logged contact found to attach this voice note to. "
                "Upload a visiting card first."
            ),
            "response_type": "text",
        }

    try:
        await update_voice_note(
            row_to_update,
            state["audio_url"],
            state["audio_transcript"]
        )

        contact_name = "the contact"
        if session and session.last_contact:
            contact_name = session.last_contact.get("name", "the contact")

        return {
            **state,
            "response_message": (
                f"🎙️ Voice note saved!\n\n"
                f"📝 **Transcript:** {state['audio_transcript']}\n\n"
                f"🔗 **Audio URL:** {state['audio_url']}\n\n"
                f"✅ Google Sheets updated for **{contact_name}**."
            ),
            "response_type": "text",
        }

    except Exception as e:
        logger.error(f"Voice note update error: {e}")
        return {
            **state,
            "error": str(e),
            "response_message": "❌ Failed to update the contact with the voice note.",
            "response_type": "text",
        }


async def respond_node(state: AgentState) -> AgentState:
    if state.get("response_message"):
        return state

    return {
        **state,
        "response_message": (
            "👋 Hi! I'm your visiting card assistant.\n\n"
            "📷 Upload a **card image** → I'll extract and save the contact\n"
            "🎙️ Upload a **voice note** → I'll transcribe and attach it to the last contact\n\n"
            "Start by uploading a visiting card!"
        ),
        "response_type": "text",
    }
