# Word → PDF Converter App

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

## Run backend locally without Docker

From the project root run:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

This ensures Python resolves the `backend` package correctly.

## API endpoints

- `POST /api/upload` — upload a DOCX file
- `GET /api/status/{job_id}` — check conversion progress
- `GET /api/download/{job_id}` — download the generated PDF after completion
