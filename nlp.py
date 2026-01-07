from __future__ import annotations
from typing import Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect, DetectorFactory

_analyzer = SentimentIntensityAnalyzer()
DetectorFactory.seed = 0

LANG_CODES = {
    "auto": "auto",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
}


def analyze_sentiment(text: str) -> str:
    if not text:
        return "neutral"
    s = _analyzer.polarity_scores(text)
    c = s.get("compound", 0)
    if c >= 0.2:
        return "positive"
    if c <= -0.2:
        return "negative"
    return "neutral"


def detect_language_code(text: str) -> Optional[str]:
    try:
        code = detect(text)
        return code
    except Exception:
        return None
