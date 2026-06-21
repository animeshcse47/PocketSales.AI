import json
import asyncio
import uuid
from datetime import datetime
from typing import Optional, Tuple

import gspread
from google.oauth2.service_account import Credentials

from app.config import settings
from app.models.contact import ContactCard

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_HEADERS = [
    "ID", "Name", "Phone", "Email", "Company", "Designation",
    "Address", "Website", "LinkedIn", "Voice Note URL",
    "Voice Transcript", "Session ID", "Logged At",
]


def _get_sheet():
    creds_dict = json.loads(settings.google_service_account_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(settings.google_sheet_id)

    try:
        ws = spreadsheet.worksheet(settings.google_sheet_name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=settings.google_sheet_name, rows=1000, cols=20)
        ws.append_row(SHEET_HEADERS)
        return ws

    existing = ws.row_values(1)
    if not existing or existing[0] != "ID":
        ws.insert_row(SHEET_HEADERS, 1)

    return ws


def _normalize_phone(phone: str) -> str:
    return "".join(filter(str.isdigit, phone or ""))


async def check_duplicate(contact: ContactCard) -> Tuple[bool, Optional[int]]:
    loop = asyncio.get_event_loop()
    ws = await loop.run_in_executor(None, _get_sheet)
    records = await loop.run_in_executor(None, ws.get_all_records)

    for i, record in enumerate(records):
        row_num = i + 2

        if contact.email and record.get("Email", "").lower() == contact.email.lower():
            return True, row_num

        if contact.phone:
            norm_incoming = _normalize_phone(contact.phone)
            norm_existing = _normalize_phone(str(record.get("Phone", "")))
            if norm_incoming and norm_incoming == norm_existing:
                return True, row_num

    return False, None


async def write_contact(contact: ContactCard, session_id: str) -> int:
    loop = asyncio.get_event_loop()
    ws = await loop.run_in_executor(None, _get_sheet)

    contact_id = str(uuid.uuid4())[:8].upper()
    row_data = [
        contact_id,
        contact.name or "",
        contact.phone or "",
        contact.email or "",
        contact.company or "",
        contact.designation or "",
        contact.address or "",
        contact.website or "",
        contact.linkedin or "",
        "",
        "",
        session_id,
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    ]

    await loop.run_in_executor(None, ws.append_row, row_data)

    all_values = await loop.run_in_executor(None, ws.get_all_values)
    return len(all_values)


async def update_voice_note(row_number: int, audio_url: str, transcript: str):
    loop = asyncio.get_event_loop()
    ws = await loop.run_in_executor(None, _get_sheet)

    headers = await loop.run_in_executor(None, ws.row_values, 1)
    voice_url_col = headers.index("Voice Note URL") + 1
    transcript_col = headers.index("Voice Transcript") + 1

    await loop.run_in_executor(None, ws.update_cell, row_number, voice_url_col, audio_url)
    await loop.run_in_executor(None, ws.update_cell, row_number, transcript_col, transcript)
