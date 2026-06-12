"""CRUD operations for file and job records."""

import uuid
from datetime import datetime

from backend.app.db.database import SessionLocal
from backend.app.models.file_model import FileRecord
from backend.app.models.job_model import Job

def create_file_record(filename: str, path: str) -> FileRecord:
    db = SessionLocal()
    try:
        record = FileRecord(id=str(uuid.uuid4()), filename=filename, path=path)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()

def create_job(filename: str, input_path: str) -> Job:
    db = SessionLocal()
    try:
        file_record = create_file_record(filename, input_path)
        job = Job(
            id=str(uuid.uuid4()),
            status="pending",
            input_path=input_path,
            output_path=None,
            error_message=None,
            file_id=file_record.id,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()

def get_job_by_id(job_id: str) -> Job | None:
    db = SessionLocal()
    try:
        return db.query(Job).filter(Job.id == job_id).first()
    finally:
        db.close()

def update_job_status(job_id: str, status: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        job.status = status
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()

def mark_job_done(job_id: str, output_path: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        job.status = "done"
        job.output_path = output_path
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()

def mark_job_failed(job_id: str, error_message: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        job.status = "failed"
        job.error_message = error_message
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()