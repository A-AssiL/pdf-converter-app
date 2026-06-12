"""Source file for annotate_comments.py."""

from pathlib import Path
import re

root = Path(__file__).resolve().parent
file_paths = sorted(
    [p for p in root.rglob('*') if p.is_file() and p.suffix in {'.py', '.js', '.jsx', '.html', '.yml', '.yaml'} or p.name == 'Dockerfile']
)

known = {
    'backend/app/main.py': 'FastAPI application entrypoint configuring CORS, routes, and startup behaviors.',
    'backend/app/api/__init__.py': 'Package initializer for backend API routers.',
    'backend/app/api/routers/upload.py': 'Upload router receives Word documents and creates conversion jobs.',
    'backend/app/api/routers/status.py': 'Status router returns job progress and download links.',
    'backend/app/api/routers/download.py': 'Download router serves completed PDF files.',
    'backend/app/core/config.py': 'Application settings and environment configuration.',
    'backend/app/core/logging.py': 'Logging configuration helper for the backend.',
    'backend/app/core/exceptions.py': 'Custom exceptions used by conversion tasks.',
    'backend/app/services/file_service.py': 'Service that stores uploaded files and ensures directories exist.',
    'backend/app/services/job_service.py': 'Service for creating and updating conversion job records.',
    'backend/app/services/parser_service.py': 'Service for extracting text from Word documents.',
    'backend/app/services/pdf_service.py': 'Service for generating PDF documents from extracted text.',
    'backend/app/utils/file_utils.py': 'Utility helpers for safe filenames and directory creation.',
    'backend/app/db/database.py': 'Database engine, session factory, and initialization helpers.',
    'backend/app/db/crud.py': 'CRUD operations for job and file records in the database.',
    'backend/app/models/job_model.py': 'SQLAlchemy model representing conversion jobs.',
    'backend/app/models/file_model.py': 'SQLAlchemy model representing uploaded file metadata.',
    'backend/app/schemas/upload_schema.py': 'Pydantic schema for upload payloads.',
    'backend/app/schemas/response_schema.py': 'Pydantic schemas for API response payloads.',
    'backend/app/workers/celery_app.py': 'Celery application instance configured with Redis broker and backend.',
    'backend/app/workers/tasks.py': 'Celery tasks that run the document conversion pipeline.',
    'worker/celery_worker.py': 'Celery worker entrypoint for starting the worker process.',
    'worker/pipeline/extractor.py': 'Pipeline stage that extracts text from DOCX documents.',
    'worker/pipeline/normalizer.py': 'Pipeline stage that normalizes extracted text.',
    'worker/pipeline/renderer.py': 'Pipeline stage that renders normalized text into a PDF file.',
    'worker/pipeline/optimizer.py': 'Pipeline stage that finalizes or optimizes the generated PDF.',
    'worker/__init__.py': 'Worker package initializer.',
    'worker/pipeline/__init__.py': 'Worker pipeline package initializer.',
    'backend/app/__init__.py': 'Backend application package initializer.',
    'frontend/src/index.jsx': 'Frontend application entrypoint that renders the React app.',
    'frontend/src/App.jsx': 'Root React application component.',
    'frontend/src/pages/Home.jsx': 'Home page component that handles upload flow and status polling.',
    'frontend/src/components/UploadBox.jsx': 'Component for selecting and uploading Word documents.',
    'frontend/src/components/ProgressBar.jsx': 'Component that visualizes conversion progress.',
    'frontend/src/components/DownloadButton.jsx': 'Component that renders the PDF download button.',
    'frontend/src/services/api.js': 'API helper functions for uploading files and polling job status.',
    'frontend/public/index.html': 'HTML shell for the React frontend app.',
    'frontend/index.html': 'HTML entrypoint for the frontend app.',
    'frontend/vite.config.js': 'Vite configuration for the frontend development server.',
    'docker-compose.yml': 'Docker Compose configuration for backend, worker, Redis, and frontend services.',
    'backend/Dockerfile': 'Dockerfile for building the backend service image.',
    'README.md': 'Project README document.',
    'fill_project.py': 'Utility script for scaffolding or filling sample project files.',
}


# Function get_desc in this module.
def get_desc(rel_path):
    rel = str(rel_path).replace('\\', '/')
    return known.get(rel, f'Source file for {rel}.')


# Function add_py_header in this module.
def add_py_header(text, desc):
    lines = text.splitlines()
    first_nonblank = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first_nonblank is None:
        return f'"""{desc}"""\n'
    if not re.match(r'^\s*(?:"""|\'\'\')', lines[first_nonblank]):
        lines.insert(first_nonblank, f'"""{desc}"""')
        lines.insert(first_nonblank + 1, '')
    return '\n'.join(lines)


# Function add_simple_docstrings in this module.
def add_simple_docstrings(text):
    lines = text.splitlines()
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        output.append(line)
        if re.match(r'^(async\s+def|def|class)\s+', line):
            indent = re.match(r'^(\s*)', line).group(1)
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                output.append(lines[j])
                j += 1
            if j < len(lines) and re.match(r'^\s*(?:"""|\'\'\'|#)', lines[j]):
                i += 1
                continue
            doc_indent = indent + '    '
            output.append(f'{doc_indent}"""{line.strip().split()[1].split("(")[0]} function."""')
            i += 1
            continue
        i += 1
    return '\n'.join(output)


# Function annotate_py in this module.
def annotate_py(text, desc):
    annotated = add_py_header(text, desc)
    return add_simple_docstrings(annotated)


# Function annotate_js in this module.
def annotate_js(text, desc):
    if not text.lstrip().startswith('//') and not text.lstrip().startswith('/*'):
        text = f'// {desc}\n\n' + text
    text = re.sub(r'^(const\s+API_BASE\s*=)', r'// Base API URL for backend requests\n\1', text, flags=re.MULTILINE)
    text = re.sub(r'^(export default function\s+[A-Za-z_]\w*\s*\()', r'// Exported React component\n\1', text, flags=re.MULTILINE)
    text = re.sub(r'^(export async function\s+[A-Za-z_]\w*\s*\()', r'// Exported async function\n\1', text, flags=re.MULTILINE)
    text = re.sub(r'^(export function\s+[A-Za-z_]\w*\s*\()', r'// Exported function\n\1', text, flags=re.MULTILINE)
    return text


# Function annotate_html in this module.
def annotate_html(text, desc):
    if '<!DOCTYPE html>' in text:
        if '<!--' not in text.splitlines()[0]:
            return text.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- ' + desc + ' -->', 1)
    if not text.lstrip().startswith('<!--'):
        return '<!-- ' + desc + ' -->\n' + text
    return text


# Function annotate_yaml in this module.
def annotate_yaml(text, desc):
    if not text.lstrip().startswith('#'):
        return '# ' + desc + '\n' + text
    return text


# Function annotate_docker in this module.
def annotate_docker(text, desc):
    if not text.lstrip().startswith('#'):
        return '# ' + desc + '\n' + text
    return text


for path in file_paths:
    rel = path.relative_to(root)
    desc = get_desc(rel)
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.py':
        new_text = annotate_py(text, desc)
    elif path.suffix in {'.js', '.jsx'}:
        new_text = annotate_js(text, desc)
    elif path.suffix == '.html':
        new_text = annotate_html(text, desc)
    elif path.suffix in {'.yml', '.yaml'}:
        new_text = annotate_yaml(text, desc)
    elif path.name == 'Dockerfile':
        new_text = annotate_docker(text, desc)
    else:
        new_text = text
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        print(f'Annotated {rel}')