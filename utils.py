from __future__ import annotations
import re
from typing import Dict, Any

END_KEYWORDS = {"bye", "exit", "quit", "stop", "end", "thank you", "thanks"}


def is_end_message(text: str) -> bool:
    t = text.strip().lower()
    return any(kw in t for kw in END_KEYWORDS)


def normalize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    p = {k: (v.strip() if isinstance(v, str) else v) for k, v in (profile or {}).items()}
    if p.get("years_of_experience"):
        try:
            p["years_of_experience"] = float(str(p["years_of_experience"]).replace(",", "."))
        except Exception:
            pass
    return p


TECH_SEPARATORS = re.compile(r"[,/|;]+|\band\b|\+", re.IGNORECASE)


def parse_tech_stack(text: str) -> list[str]:
    if not text:
        return []
    parts = [s.strip() for s in TECH_SEPARATORS.split(text) if s.strip()]
    # Deduplicate keeping order
    seen = set()
    out = []
    for s in parts:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out
