"""Pipeline stage that normalizes extracted text."""

import re

def normalize(text: str) -> str:
    normalized = re.sub(r"\r\n", "\n", text)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    return normalized.strip()