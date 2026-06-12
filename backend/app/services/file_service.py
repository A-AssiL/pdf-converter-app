"""Service for saving uploaded files to disk."""

import shutil
from pathlib import Path
from fastapi import UploadFile

from backend.app.core.config import Settings
from backend.app.utils.file_utils import create_directories, make_safe_filename

class FileService:

    def __init__(self, settings: Settings):
        self.settings = settings
        create_directories(self.settings.upload_dir, self.settings.processed_dir, self.settings.temp_dir)

    async def save_upload(self, upload_file: UploadFile) -> dict:
        safe_name = make_safe_filename(upload_file.filename)
        destination = self.settings.upload_dir / safe_name
        content = await upload_file.read()
        destination.write_bytes(content)
        return {
            "filename": safe_name,
            "filepath": str(destination),
        }