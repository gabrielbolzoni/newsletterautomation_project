import requests
import json
import os

def get_senders():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    response = requests.get(
        f"{supabase_url}/rest/v1/newsletters_senders",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
        params={
            "is_active": "eq.true",
            "select": "email"
        }
    )
    response.raise_for_status()
    data = response.json()

    return [row["email"] for row in data]

def get_audio_config():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    response = requests.get(
        f"{supabase_url}/rest/v1/audio_settings",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
        params={
            "is_active": "eq.true",
            "limit": 1
        }
    )
    response.raise_for_status()
    data = response.json()[0]

    return {
        "model": data["model"],
        "voice": data["voice"],
        "speed": float(data["speed"]),
    }
