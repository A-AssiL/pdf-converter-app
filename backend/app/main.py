import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ root = /app داخل Docker
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ✅ IMPORTANT: استيراد صحيح حسب الهيكل backend.app
from backend.app.api.routers import download as download_router
from backend.app.api.routers import status as status_router
from backend.app.api.routers import upload as upload_router
from backend.app.db.database import init_db
from backend.app.core.config import Settings

settings = Settings()

app = FastAPI(
    title="Word to PDF Converter",
    description="Upload DOCX → Celery worker → PDF download",
    version="1.0.0",
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Startup ----------------
@app.on_event("startup")
def on_startup():
    init_db()

# ---------------- Routers ----------------
app.include_router(upload_router.router, prefix="/api/upload", tags=["upload"])
app.include_router(status_router.router, prefix="/api/status", tags=["status"])
app.include_router(download_router.router, prefix="/api/download", tags=["download"])

# ---------------- Health ----------------
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "pdf-converter"
    }