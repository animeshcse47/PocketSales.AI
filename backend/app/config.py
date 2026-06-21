from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    google_service_account_json: str
    google_sheet_id: str
    google_sheet_name: str = "Contacts"
    google_drive_folder_id: str = ""

    mongodb_uri: str

    whatsapp_provider: str = "twilio"
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_access_token: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None
    manager_whatsapp_number: str

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_public_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "changeme"
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
