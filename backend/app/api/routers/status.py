"""Status router for checking conversion progress and download URLs."""

from fastapi import APIRouter, HTTPException

from backend.app.services.job_service import JobService
from backend.app.schemas.response_schema import StatusResponse
from backend.app.core.config import Settings

settings = Settings()
job_service = JobService(settings=settings)
router = APIRouter()

@router.get("/{job_id}", response_model=StatusResponse)

def get_status(job_id: str):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    download_url = None
    if job.status == "done":
        download_url = f"/api/download/{job.id}"

    return StatusResponse(
        job_id=job.id,
        status=job.status,
        download_url=download_url,
        error=job.error_message,
    )