import json
import os
from datetime import datetime
from typing import Any, Dict
import hashlib

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_PATH = os.path.join(DATA_DIR, "candidates.jsonl")

os.makedirs(DATA_DIR, exist_ok=True)


def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    masked_name = name[0] + "***" if name else "***"
    return f"{masked_name}@{domain}"


def mask_phone(phone: str) -> str:
    if not phone:
        return phone
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) <= 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def hash_email(email: str) -> str | None:
    if not email:
        return None
    norm = email.strip().lower()
    if not norm:
        return None
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def persist_candidate(session_id: str, profile: Dict[str, Any], chat_transcript: list[Dict[str, str]]) -> None:
    hashed_email = hash_email(profile.get("email", ""))
    record = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "hashed_email": hashed_email,
        "profile": {
            **profile,
            "email": mask_email(profile.get("email", "")),
            "phone": mask_phone(profile.get("phone", "")),
        },
        "transcript": chat_transcript,
    }
    with open(DATA_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_last_profile(hashed_email: str | None) -> Dict[str, Any] | None:
    if not hashed_email or not os.path.exists(DATA_PATH):
        return None
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in reversed(lines):
            try:
                obj = json.loads(line)
                if obj.get("hashed_email") == hashed_email:
                    return obj.get("profile")
            except Exception:
                continue
    except Exception:
        return None
    return None
