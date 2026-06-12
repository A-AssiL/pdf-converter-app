from docx import Document


def extract(docx_path: str) -> str:
    document = Document(docx_path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n\n".join(paragraphs)
