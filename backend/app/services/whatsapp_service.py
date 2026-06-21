import asyncio
import httpx
from app.config import settings
from app.models.contact import ContactCard


def _build_message(contact: ContactCard) -> str:
    return (
        f"📇 *New Visiting Card Logged!*\n\n"
        f"👤 *Name:* {contact.name}\n"
        f"🏢 *Company:* {contact.company or 'N/A'}\n"
        f"📧 *Email:* {contact.email or 'N/A'}\n"
        f"📞 *Phone:* {contact.phone or 'N/A'}\n"
        f"💼 *Designation:* {contact.designation or 'N/A'}\n\n"
        f"✅ Contact saved to Google Sheets."
    )


async def send_whatsapp_notification(contact: ContactCard):
    message = _build_message(contact)

    if settings.whatsapp_provider == "meta":
        await _send_via_meta(message)
    else:
        await _send_via_twilio(message)


async def _send_via_meta(message: str):
    url = f"https://graph.facebook.com/v19.0/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.manager_whatsapp_number,
        "type": "text",
        "text": {"body": message},
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()


def _twilio_send_sync(message: str):
    from twilio.rest import Client
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    client.messages.create(
        body=message,
        from_=settings.twilio_whatsapp_number,
        to=f"whatsapp:{settings.manager_whatsapp_number}",
    )


async def _send_via_twilio(message: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _twilio_send_sync, message)
