"""Source file for backend/app/utils/pdf_utils.py."""

from reportlab.lib.pagesizes import letter
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