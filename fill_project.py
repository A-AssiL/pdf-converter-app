"""Source file for fill_project.py."""

﻿from pathlib import Path
files = {
    "backend/app/main.py": '''from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routers import download as download_router
from backend.app.api.routers import status as status_router
from backend.app.api.routers import upload as upload_router
from backend.app.db.database import init_db
from backend.app.core.config import Settings

settings = Settings()

app = FastAPI(
    title="Word to PDF Converter",
    description="Upload a DOCX file, process it with a worker pipeline, and download the generated PDF.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

@app.on_event("startup")
# Function on_startup in this module.
def on_startup():
    init_db()

app.include_router(upload_router.router, prefix="/api/upload", tags=["upload"])
app.include_router(status_router.router, prefix="/api/status", tags=["status"])
app.include_router(download_router.router, prefix="/api/download", tags=["download"])

@app.get("/api/health")
# Function health_check in this module.
def health_check():
    return {"status": "ok", "service": "pdf-converter"}
''',

    "backend/app/api/__init__.py": '''# API package for backend routes
''',

    "backend/app/api/routers/upload.py": '''import uuid

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
# Function def in this module.
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
''',

    "backend/app/api/routers/status.py": '''from fastapi import APIRouter, HTTPException

from backend.app.services.job_service import JobService
from backend.app.schemas.response_schema import StatusResponse
from backend.app.core.config import Settings

settings = Settings()
job_service = JobService(settings=settings)
router = APIRouter()

@router.get("/{job_id}", response_model=StatusResponse)
# Function get_status in this module.
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
''',

    "backend/app/api/routers/download.py": '''import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.services.job_service import JobService
from backend.app.core.config import Settings

settings = Settings()
job_service = JobService(settings=settings)
router = APIRouter()

@router.get("/{job_id}")
# Function download_pdf in this module.
def download_pdf(job_id: str):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "done" or not job.output_path:
        raise HTTPException(status_code=400, detail="PDF is not ready yet.")
    if not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Output file not found.")

    return FileResponse(job.output_path, filename=os.path.basename(job.output_path), media_type="application/pdf")
''',

    "backend/app/core/config.py": '''from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[3]

# Class Settings in this module.
class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    redis_url: str = "redis://redis:6379/0"
    result_backend: str = "redis://redis:6379/1"
    database_url: str = "sqlite:///./backend/app/db/app.db"
    upload_dir: Path = BASE_DIR / "storage" / "uploads"
    processed_dir: Path = BASE_DIR / "storage" / "processed"
    temp_dir: Path = BASE_DIR / "storage" / "temp"

# Class Config: in this module.
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
''',

    "backend/app/core/logging.py": '''import logging

from logging.config import dictConfig

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


# Function setup_logging in this module.
def setup_logging():
    dictConfig(LOG_CONFIG)
''',

    "backend/app/core/exceptions.py": '''class ConversionError(Exception):
    """Raised when a document conversion step fails."""
    pass
''',

    "backend/app/services/file_service.py": '''import shutil
from pathlib import Path
from fastapi import UploadFile

from backend.app.core.config import Settings
from backend.app.utils.file_utils import create_directories, make_safe_filename


# Class FileService: in this module.
class FileService:
# Function __init__ in this module.
    def __init__(self, settings: Settings):
        self.settings = settings
        create_directories(self.settings.upload_dir, self.settings.processed_dir, self.settings.temp_dir)

# Function def in this module.
    async def save_upload(self, upload_file: UploadFile) -> dict:
        safe_name = make_safe_filename(upload_file.filename)
        destination = self.settings.upload_dir / safe_name
        content = await upload_file.read()
        destination.write_bytes(content)
        return {
            "filename": safe_name,
            "filepath": str(destination),
        }
''',

    "backend/app/services/job_service.py": '''from backend.app.core.config import Settings
from backend.app.db import crud

# Class JobService: in this module.
class JobService:
# Function __init__ in this module.
    def __init__(self, settings: Settings):
        self.settings = settings

# Function create_job in this module.
    def create_job(self, original_filename: str, upload_path: str):
        return crud.create_job(original_filename, upload_path)

# Function get_job in this module.
    def get_job(self, job_id: str):
        return crud.get_job_by_id(job_id)

# Function mark_job_processing in this module.
    def mark_job_processing(self, job_id: str):
        return crud.update_job_status(job_id, "processing")

# Function mark_job_done in this module.
    def mark_job_done(self, job_id: str, output_path: str):
        return crud.mark_job_done(job_id, output_path)

# Function mark_job_failed in this module.
    def mark_job_failed(self, job_id: str, error_message: str):
        return crud.mark_job_failed(job_id, error_message)
''',

    "backend/app/services/parser_service.py": '''from docx import Document


# Class ParserService: in this module.
class ParserService:
# Function extract_text in this module.
    def extract_text(self, file_path: str) -> str:
        document = Document(file_path)
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n\n".join(paragraphs)
''',

    "backend/app/services/pdf_service.py": '''from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch


# Class PDFService: in this module.
class PDFService:
# Function create_pdf in this module.
    def create_pdf(self, text: str, output_path: str):
        pdf = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        story = []

        for paragraph in text.split('\n\n'):
            story.append(Paragraph(paragraph.replace('\n', '<br/>'), styles['BodyText']))
            story.append(Spacer(1, 12))

        pdf.build(story)
''',

    "backend/app/workers/celery_app.py": '''from celery import Celery

from backend.app.core.config import Settings

settings = Settings()
celery_app = Celery(
    "pdf_converter",
    broker=settings.redis_url,
    backend=settings.result_backend,
    include=["backend.app.workers.tasks"],
)
celery_app.conf.task_routes = {
    "backend.app.workers.tasks.process_document": {"queue": "pdf_tasks"}
}
''',

    "backend/app/workers/tasks.py": '''import os
from pathlib import Path

from backend.app.workers.celery_app import celery_app
from backend.app.core.config import Settings
from backend.app.db import crud
from backend.app.services.job_service import JobService
from worker.pipeline.extractor import extract
from worker.pipeline.normalizer import normalize
from worker.pipeline.renderer import render
from worker.pipeline.optimizer import optimize

settings = Settings()
job_service = JobService(settings=settings)


# Function _process_stage in this module.
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
# Function process_document in this module.
def process_document(job_id: str):
    try:
        _process_stage(job_id)
    except Exception as exc:
        crud.mark_job_failed(job_id, str(exc))
        raise
''',

    "backend/app/models/file_model.py": '''from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


# Class FileRecord in this module.
class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, index=True)
    filename = Column(String(260), nullable=False)
    path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="file")
''',

    "backend/app/models/job_model.py": '''from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


# Class Job in this module.
class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    input_path = Column(String(1024), nullable=False)
    output_path = Column(String(1024), nullable=True)
    error_message = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)

    file = relationship("FileRecord", back_populates="jobs")
''',

    "backend/app/schemas/upload_schema.py": '''from typing import Optional

from pydantic import BaseModel


# Class UploadSchema in this module.
class UploadSchema(BaseModel):
    notes: Optional[str] = None
''',

    "backend/app/schemas/response_schema.py": '''from typing import Optional

from pydantic import BaseModel


# Class UploadResponse in this module.
class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


# Class StatusResponse in this module.
class StatusResponse(BaseModel):
    job_id: str
    status: str
    download_url: Optional[str] = None
    error: Optional[str] = None
''',

    "backend/app/utils/file_utils.py": '''import re
from pathlib import Path


# Function make_safe_filename in this module.
def make_safe_filename(filename: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    return sanitized.strip("_ ") or "uploaded_file"


# Function create_directories in this module.
def create_directories(*paths: Path):
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
''',

    "backend/app/utils/pdf_utils.py": '''from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


# Class PDFUtils: in this module.
class PDFUtils:
# Function render_text_to_pdf in this module.
    def render_text_to_pdf(self, text: str, output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        story = []

        for paragraph in text.split("\n\n"):
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 12))

        doc.build(story)
''',

    "backend/app/db/database.py": '''from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from backend.app.core.config import Settings

settings = Settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


# Function init_db in this module.
def init_db():
    from backend.app.models.file_model import FileRecord
    from backend.app.models.job_model import Job

    Base.metadata.create_all(bind=engine)


# Function get_db in this module.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',

    "backend/app/db/crud.py": '''import uuid
from datetime import datetime

from backend.app.db.database import SessionLocal
from backend.app.models.file_model import FileRecord
from backend.app.models.job_model import Job


# Function create_file_record in this module.
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


# Function create_job in this module.
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


# Function get_job_by_id in this module.
def get_job_by_id(job_id: str) -> Job | None:
    db = SessionLocal()
    try:
        return db.query(Job).filter(Job.id == job_id).first()
    finally:
        db.close()


# Function update_job_status in this module.
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


# Function mark_job_done in this module.
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


# Function mark_job_failed in this module.
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
''',

    "backend/requirements.txt": '''fastapi
uvicorn[standard]
python-multipart
SQLAlchemy
pydantic
python-docx
reportlab
celery[redis]
redis
python-dotenv
''',

    "backend/Dockerfile": '''FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',

    "frontend/package.json": '''{
  "name": "pdf-converter-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.1"
  }
}
''',

    "frontend/vite.config.js": '''import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
''',

    "frontend/public/index.html": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Word to PDF Converter</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.js"></script>
  </body>
</html>
''',

    "frontend/src/App.js": '''import Home from "./pages/Home";

function App() {
  return <Home />;
}

export default App;
''',

    "frontend/src/index.js": '''import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''',

    "frontend/src/components/UploadBox.jsx": '''import { useState } from "react";

export default function UploadBox({ onUpload }) {
  const [selectedFile, setSelectedFile] = useState(null);

  return (
    <div style={{ padding: 16, border: "1px solid #ddd", borderRadius: 12, maxWidth: 520, margin: "0 auto" }}>
      <label style={{ display: "block", marginBottom: 8, fontWeight: 600 }}>
        Upload DOCX file
      </label>
      <input
        type="file"
        accept=".doc,.docx"
        onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
        style={{ marginBottom: 12 }}
      />
      <button
        disabled={!selectedFile}
        onClick={() => onUpload(selectedFile)}
        style={{ padding: "10px 20px", borderRadius: 8, border: "none", background: "#2563eb", color: "#fff", cursor: "pointer" }}
      >
        Upload and Convert
      </button>
    </div>
  );
}
''',

    "frontend/src/components/ProgressBar.jsx": '''export default function ProgressBar({ status }) {
  const label = status === "pending" ? "Waiting for worker..." : status === "processing" ? "Processing document..." : status === "done" ? "Ready to download" : "Failed";
  return (
    <div style={{ marginTop: 20, textAlign: "center" }}>
      <div style={{ marginBottom: 8, fontWeight: 600 }}>{label}</div>
      <div style={{ height: 12, width: "100%", background: "#e5e7eb", borderRadius: 8 }}>
        <div
          style={{
            height: "100%",
            width: status === "done" ? "100%" : status === "processing" ? "70%" : status === "pending" ? "40%" : "100%",
            background: status === "failed" ? "#ef4444" : "#2563eb",
            borderRadius: 8,
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
}
''',

    "frontend/src/components/DownloadButton.jsx": '''export default function DownloadButton({ url }) {
  if (!url) {
    return null;
  }

  return (
    <div style={{ marginTop: 20, textAlign: "center" }}>
      <a
        href={url}
        download
        style={{ display: "inline-block", padding: "10px 20px", background: "#10b981", color: "#fff", borderRadius: 8, textDecoration: "none" }}
      >
        Download PDF
      </a>
    </div>
  );
}
''',

    "frontend/src/pages/Home.jsx": '''import { useEffect, useState } from "react";
import UploadBox from "../components/UploadBox";
import ProgressBar from "../components/ProgressBar";
import DownloadButton from "../components/DownloadButton";
import { getJobStatus, uploadDocument } from "../services/api";

export default function Home() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval = null;

    if (jobId && status && status !== "done" && status !== "failed") {
      interval = setInterval(async () => {
        const response = await getJobStatus(jobId);
        setStatus(response.status);
        setDownloadUrl(response.download_url);
        setError(response.error);
      }, 2000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [jobId, status]);

  async function handleUpload(file) {
    setError(null);
    setMessage("Uploading file...");
    setStatus("pending");
    setDownloadUrl(null);

    try {
      const result = await uploadDocument(file);
      setJobId(result.job_id);
      setStatus(result.status);
      setMessage(result.message);
    } catch (err) {
      setError(err.message || "Upload failed.");
      setStatus("failed");
    }
  }

  return (
    <div style={{ fontFamily: "Inter, sans-serif", minHeight: "100vh", background: "#f8fafc", padding: 24 }}>
      <div style={{ maxWidth: 760, margin: "0 auto", background: "#fff", padding: 32, borderRadius: 24, boxShadow: "0 20px 60px rgba(0,0,0,.08)" }}>
        <h1 style={{ marginBottom: 16 }}>Word to PDF Converter</h1>
        <p style={{ lineHeight: 1.8, color: "#374151" }}>
          Upload a DOCX document and let the worker pipeline convert it into a downloadable PDF file.
        </p>

        <UploadBox onUpload={handleUpload} />

        {message && <p style={{ marginTop: 20 }}>{message}</p>}
        {status && <ProgressBar status={status} />}
        {error && <p style={{ marginTop: 12, color: "#dc2626" }}>{error}</p>}
        {downloadUrl && <DownloadButton url={downloadUrl} />}
      </div>
    </div>
  );
}
''',

    "frontend/src/services/api.js": '''const API_BASE = "/api";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Upload failed");
  }

  return response.json();
}

export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE}/status/${jobId}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Could not fetch status.");
  }
  return response.json();
}
''',

    "worker/requirements.txt": '''celery[redis]
redis
python-docx
reportlab
python-dotenv
SQLAlchemy
''',

    "worker/celery_worker.py": '''from backend.app.workers.celery_app import celery_app

if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info", "--concurrency=1"]) 
''',

    "worker/pipeline/extractor.py": '''from docx import Document


# Function extract in this module.
def extract(docx_path: str) -> str:
    document = Document(docx_path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n\n".join(paragraphs)
''',

    "worker/pipeline/normalizer.py": '''import re


# Function normalize in this module.
def normalize(text: str) -> str:
    normalized = re.sub(r"\r\n", "\n", text)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    return normalized.strip()
''',

    "worker/pipeline/renderer.py": '''from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


# Function render in this module.
def render(text: str, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []

    for paragraph in text.split("\n\n"):
        story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 12))

    doc.build(story)
''',

    "worker/pipeline/optimizer.py": '''import shutil


# Function optimize in this module.
def optimize(input_path: str, output_path: str):
    shutil.copyfile(input_path, output_path)
''',

    "config/app.env": '''API_HOST=0.0.0.0
API_PORT=8000
REDIS_URL=redis://redis:6379/0
RESULT_BACKEND=redis://redis:6379/1
DATABASE_URL=sqlite:///./backend/app/db/app.db
UPLOAD_DIR=/app/storage/uploads
PROCESSED_DIR=/app/storage/processed
TEMP_DIR=/app/storage/temp
''',

    "config/redis.conf": '''bind 0.0.0.0
port 6379
save 900 1
save 300 10
save 60 10000
maxmemory 256mb
maxmemory-policy allkeys-lru
''',

    "docker-compose.yml": '''version: "3.9"

services:
  redis:
    image: redis:7-alpine
    volumes:
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file:
      - ./config/app.env
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis

  worker:
    image: python:3.12-slim
    env_file:
      - ./config/app.env
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./:/app
    working_dir: /app
    depends_on:
      - redis
    command: ["sh", "-c", "pip install --no-cache-dir -r /app/worker/requirements.txt && python /app/worker/celery_worker.py"]

  frontend:
    image: node:20-alpine
    working_dir: /app/frontend
    volumes:
      - ./frontend:/app/frontend
    ports:
      - "5173:5173"
    command: ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0 --port 5173"]
''',

    "README.md": '''# Word → PDF Converter App

This repository contains a production-ready MVP for a DOCX to PDF conversion web application using FastAPI, Celery, Redis, and a React frontend.

## Project structure

- `backend/` — API layer and job orchestration
- `worker/` — Celery worker and conversion pipeline
- `frontend/` — React/Vite web UI
- `storage/` — local file storage for uploads, temporary files, and processed PDFs
- `config/` — Redis and environment configuration

## Run locally with Docker Compose

```bash
docker compose up --build
```

Then open:

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## API endpoints

- `POST /api/upload` — upload a DOCX file
- `GET /api/status/{job_id}` — check conversion progress
- `GET /api/download/{job_id}` — download the generated PDF after completion
''',

    "worker/__init__.py": '''# Worker package root''',
    "worker/pipeline/__init__.py": '''# Worker pipeline package''',
}

for path, content in files.items():
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

print("Wrote all project files successfully.")