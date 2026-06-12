"""Service for managing job lifecycle operations."""

from backend.app.core.config import Settings
from backend.app.db import crud

class JobService:

    def __init__(self, settings: Settings):
        self.settings = settings

    def create_job(self, original_filename: str, upload_path: str):
        return crud.create_job(original_filename, upload_path)

    def get_job(self, job_id: str):
        return crud.get_job_by_id(job_id)

    def mark_job_processing(self, job_id: str):
        return crud.update_job_status(job_id, "processing")

    def mark_job_done(self, job_id: str, output_path: str):
        return crud.mark_job_done(job_id, output_path)

    def mark_job_failed(self, job_id: str, error_message: str):
        return crud.mark_job_failed(job_id, error_message)