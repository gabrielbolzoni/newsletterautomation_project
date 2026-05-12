import os
import re
import requests
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, field_validator


class AudioListRecord(BaseModel):
    sender: str
    title: str
    main_topics: str
    audio_config: dict[str, Any]
    created_at: datetime

    @field_validator("sender")
    @classmethod
    def clean_and_validate_sender(cls, v):
        # Remove emojis e caracteres não ASCII
        v = re.sub(r'[^\x00-\x7F]+', '', v).strip()
        # Remove caracteres especiais que possam vir junto ao email (ex: *, •, >)
        v = re.sub(r'[^\w@.\-+]', '', v).strip()
        if "@" not in v:
            raise ValueError(f"sender deve ser um email válido, recebido: {v}")
        return v

    @field_validator("title", "main_topics")
    @classmethod
    def must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Campo não pode ser vazio")
        return v

    @field_validator("audio_config")
    @classmethod
    def config_must_have_required_keys(cls, v):
        required = {"model", "voice", "speed"}
        missing = required - v.keys()
        if missing:
            raise ValueError(f"audio_config faltando chaves: {missing}")
        return v


def table_insert(news: dict, cleaned_content: dict, audio_config: dict):
    """
    Validates and inserts a single audio metadata record into the Supabase audio_list table.

    Args:
        news (dict): raw email data containing the sender field
        cleaned_content (dict): filtered newsletter content with newsletter title and main_topics
        audio_config (dict): TTS model configuration used to generate the audio
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    record = AudioListRecord(
        sender=news["sender"],
        title=cleaned_content["title"],
        main_topics=cleaned_content["main_topics"],
        audio_config=audio_config,
        created_at=datetime.now(timezone.utc),
    )

    response = requests.post(
        f"{supabase_url}/rest/v1/audios_list",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        json=record.model_dump(mode="json"),
    )
    response.raise_for_status()