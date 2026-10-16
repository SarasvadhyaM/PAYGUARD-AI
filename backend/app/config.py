import os
from typing import Optional


class Settings:
    app_name: str = "PayGuard AI"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    allowed_message_length: int = int(os.getenv("ALLOWED_MESSAGE_LENGTH", "600"))
    llm_provider: str = os.getenv("LLM_PROVIDER", "none").strip().lower()
    llm_model: str = os.getenv("LLM_MODEL", "gpt-oss:20b").strip()
    llm_api_base: Optional[str] = os.getenv("LLM_API_BASE")
    llm_api_key: Optional[str] = os.getenv("LLM_API_KEY")
    llm_api_key_header: str = os.getenv("LLM_API_KEY_HEADER", "Authorization")


settings = Settings()
