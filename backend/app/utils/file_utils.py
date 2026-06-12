"""Utility helpers for safe filenames and directory creation."""

import re
from pathlib import Path

def make_safe_filename(filename: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    return sanitized.strip("_ ") or "uploaded_file"

def create_directories(*paths: Path):
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)