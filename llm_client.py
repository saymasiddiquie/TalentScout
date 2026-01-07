import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
DEFAULT_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def chat_completion(messages: List[Dict], model: str | None = None, temperature: float = 0.3, max_tokens: int = 600) -> str:
    model = model or DEFAULT_MODEL
    try:
        client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE),
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"[LLM error] {e}"
