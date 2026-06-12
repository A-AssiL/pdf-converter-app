"""Upload router to receive Word documents and enqueue conversion jobs."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.core.config import Settings
from backend.app.services.file_service import FileService
from backend.app.services.job_service import JobService
from backend.app.schemas.response_schema import UploadResponse
from backend.app.workers.tasks import process_document

settings = Settings()
file_service = FileService(settings=settings)
job_service = JobService(settings=settings)
router = APIRouter()

@router.post("/", response_model=UploadResponse)

async def upload_document(file: UploadFile = File(...)):
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Upload a DOCX or DOC file.")

    upload_data = await file_service.save_upload(file)
    job = job_service.create_job(upload_data["filename"], upload_data["filepath"])

    process_document.delay(job.id)

    return UploadResponse(
        job_id=job.id,
        status=job.status,
        message="Upload received. Conversion started.",
    )