"""Download router for serving generated PDF files."""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.services.job_service import JobService
from backend.app.core.config import Settings

settings = Settings()
job_service = JobService(settings=settings)
router = APIRouter()

@router.get("/{job_id}")

def download_pdf(job_id: str):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "done" or not job.output_path:
        raise HTTPException(status_code=400, detail="PDF is not ready yet.")
    if not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Output file not found.")

    return FileResponse(job.output_path, filename=os.path.basename(job.output_path), media_type="application/pdf")