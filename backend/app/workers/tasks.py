"""Celery tasks that orchestrate the conversion pipeline."""

from backend.app.workers.celery_app import celery_app
from backend.app.core.config import Settings
from backend.app.db import crud
from worker.pipeline.extractor import extract
from worker.pipeline.normalizer import normalize
from worker.pipeline.renderer import render
from worker.pipeline.optimizer import optimize
from backend.app.services.job_service import JobService

settings = Settings()
job_service = JobService(settings=settings)

def _process_stage(job_id: str):
    job = crud.get_job_by_id(job_id)
    if not job:
        raise ValueError("Job not found")

    crud.update_job_status(job_id, "processing")

    extracted_text = extract(job.input_path)
    normalized_text = normalize(extracted_text)

    interim_pdf_path = settings.temp_dir / f"{job_id}.pdf"
    render(normalized_text, str(interim_pdf_path))

    final_pdf_path = settings.processed_dir / f"{job_id}.pdf"
    optimize(str(interim_pdf_path), str(final_pdf_path))

    crud.mark_job_done(job_id, str(final_pdf_path))

@celery_app.task(name="backend.app.workers.tasks.process_document")

def process_document(job_id: str):
    try:
        _process_stage(job_id)
    except Exception as exc:
        crud.mark_job_failed(job_id, str(exc))
        raise