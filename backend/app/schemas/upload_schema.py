"""Pydantic schema for upload payloads."""

from typing import Optional

from pydantic import BaseModel

class UploadSchema(BaseModel):
    notes: Optional[str] = None