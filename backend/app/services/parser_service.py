"""Service for extracting text from Word documents."""

from docx import Document

class ParserService:

    def extract_text(self, file_path: str) -> str:
        document = Document(file_path)
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n\n".join(paragraphs)